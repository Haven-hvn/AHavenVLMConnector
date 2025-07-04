"""
A Haven VLM Connector
A StashApp plugin for Vision-Language Model based content tagging
"""

import os
import sys
import json
import subprocess
import shutil
import traceback
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# ----------------- Setup and Dependencies -----------------

# Use PythonDepManager for dependency management
try:
    from PythonDepManager import ensure_import
    
    # Install and ensure all required dependencies with specific versions
    ensure_import(
        "stashapi:stashapp-tools==0.2.58",
        "aiohttp==3.12.13",
        "pydantic==2.11.7",
        "vlm-engine==0.2.1",
        "pyyaml==6.0.2"
    )
    
    # Import the dependencies after ensuring they're available
    import stashapi.log as log
    from stashapi.stashapp import StashInterface
    import aiohttp
    import pydantic
    import yaml
    
except ImportError as e:
    print(f"Failed to import PythonDepManager or required dependencies: {e}")
    print("Please ensure PythonDepManager is installed and available.")
    sys.exit(1)
except Exception as e:
    print(f"Error during dependency management: {e}")
    print(f"Stack trace: {traceback.format_exc()}")
    sys.exit(1)

# Import local modules
try:
    import haven_vlm_config as config
except ModuleNotFoundError:
    log.error("Please provide a haven_vlm_config.py file with the required variables.")
    raise Exception("Please provide a haven_vlm_config.py file with the required variables.")

import haven_media_handler as media_handler
import haven_vlm_engine as vlm_engine
from haven_vlm_engine import TimeFrame

log.debug("Python instance is running at: " + sys.executable)

# ----------------- Global Variables -----------------

semaphore: Optional[asyncio.Semaphore] = None
progress: float = 0.0
increment: float = 0.0

# ----------------- Main Execution -----------------

async def main() -> None:
    """Main entry point for the plugin"""
    global semaphore
    semaphore = asyncio.Semaphore(config.config.concurrent_task_limit)
    json_input = read_json_input()
    output = {}
    await run(json_input, output)
    out = json.dumps(output)
    print(out + "\n")

def read_json_input() -> Dict[str, Any]:
    """Read JSON input from stdin"""
    json_input = sys.stdin.read()
    return json.loads(json_input)

async def run(json_input: Dict[str, Any], output: Dict[str, Any]) -> None:
    """Main execution logic"""
    plugin_args = None
    try:
        log.debug(json_input["server_connection"])
        os.chdir(json_input["server_connection"]["PluginDir"])
        media_handler.initialize(json_input["server_connection"])
    except Exception as e:
        log.error(f"Failed to initialize media handler: {e}")
        raise

    try:
        plugin_args = json_input['args']["mode"]
    except KeyError:
        pass

    if plugin_args == "tag_videos":
        await tag_videos()
        output["output"] = "ok"
        return
    elif plugin_args == "find_marker_settings":
        await find_marker_settings()
        output["output"] = "ok"
        return
    elif plugin_args == "collect_incorrect_markers":
        collect_incorrect_markers_and_images()
        output["output"] = "ok"
        return
    
    output["output"] = "ok"
    return

# ----------------- High Level Processing Functions -----------------

async def tag_videos() -> None:
    """Tag videos with VLM analysis"""
    global increment
    scenes = media_handler.get_tagme_scenes()
    if scenes:
        increment = 1.0 / len(scenes)
        tasks = [__tag_video(scene) for scene in scenes]
        await asyncio.gather(*tasks)
    else:
        log.info("No videos to tag. Have you tagged any scenes with the VLM_TagMe tag to get processed?")

async def find_marker_settings() -> None:
    """Find optimal marker settings based on a single tagged video"""
    scenes = media_handler.get_tagme_scenes()
    if len(scenes) != 1:
        log.error("Please tag exactly one scene with the VLM_TagMe tag to get processed.")
        return
    scene = scenes[0]
    await __find_marker_settings(scene)

def collect_incorrect_markers_and_images() -> None:
    """Collect data from incorrectly tagged markers and images"""
    incorrect_images = media_handler.get_incorrect_images()
    image_paths, image_ids, temp_files = media_handler.get_image_paths_and_ids(incorrect_images)
    incorrect_markers = media_handler.get_incorrect_markers()
    
    if not (len(incorrect_images) > 0 or len(incorrect_markers) > 0):
        log.info("No incorrect images or markers to collect.")
        return
    
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    try:
        # Process images
        image_folder = os.path.join(config.config.output_data_dir, "images")
        os.makedirs(image_folder, exist_ok=True)
        for image_path in image_paths:
            try:
                shutil.copy(image_path, image_folder)
            except Exception as e:
                log.error(f"Failed to copy image {image_path} to {image_folder}: {e}")
    except Exception as e:
        log.error(f"Failed to process images: {e}")
        raise e
    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                if os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                else:
                    os.remove(temp_file)
            except Exception as e:
                log.debug(f"Failed to remove temp file {temp_file}: {e}")

    # Process markers
    scene_folder = os.path.join(config.config.output_data_dir, "scenes")
    os.makedirs(scene_folder, exist_ok=True)
    tag_folders = {}
    
    for marker in incorrect_markers:
        scene_path = marker['scene']['files'][0]['path']
        if not scene_path:
            log.error(f"Marker {marker['id']} has no scene path")
            continue
        try:
            tag_name = marker['primary_tag']['name']
            if tag_name not in tag_folders:
                tag_folders[tag_name] = os.path.join(scene_folder, tag_name)
                os.makedirs(tag_folders[tag_name], exist_ok=True)
            media_handler.write_scene_marker_to_file(marker, scene_path, tag_folders[tag_name])
        except Exception as e:
            log.error(f"Failed to collect scene: {e}")
    
    # Remove incorrect tags from images
    image_ids = [image['id'] for image in incorrect_images]
    media_handler.remove_incorrect_tag_from_images(image_ids)

# ----------------- Low Level Processing Functions -----------------

async def __tag_images(images: List[Dict[str, Any]]) -> None:
    """Tag a batch of images"""
    async with semaphore:
        try:
            image_paths, image_ids, temp_files = media_handler.get_image_paths_and_ids(images)
            
            if not image_paths:
                log.warning("No valid image paths found in batch")
                return

            # Process images through VLM Engine
            results = await vlm_engine.process_images_async(
                image_paths,
                threshold=config.config.image_threshold,
                return_confidence=config.config.image_confidence_return
            )

            # Process results and add tags
            for i, result in enumerate(results.result):
                if i < len(image_ids):
                    image_id = image_ids[i]
                    detected_tags = result.get('tags', [])
                    
                    if detected_tags:
                        tag_ids = media_handler.get_tag_ids(detected_tags, create=True)
                        media_handler.add_tags_to_image(image_id, tag_ids)
                        log.info(f"Added tags {detected_tags} to image {image_id}")
                    else:
                        log.debug(f"No tags detected for image {image_id}")

            # Remove VLM_TagMe tags from processed images
            media_handler.remove_tagme_tags_from_images(image_ids)
            
        except Exception as e:
            log.error(f"Error processing image batch: {e}")
            # Add error tags to failed images
            image_ids = [img['id'] for img in images]
            media_handler.add_error_images(image_ids)
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    if os.path.isdir(temp_file):
                        shutil.rmtree(temp_file)
                    else:
                        os.remove(temp_file)
                except Exception as e:
                    log.debug(f"Failed to remove temp file {temp_file}: {e}")

async def __tag_video(scene: Dict[str, Any]) -> None:
    """Tag a single video scene"""
    async with semaphore:
        try:
            scene_id = scene['id']
            scene_file = scene['files'][0]['path']
            
            # Check if scene is VR
            is_vr = media_handler.is_vr_scene(scene['tags'])
            
            # Process video through VLM Engine
            video_result = await vlm_engine.process_video_async(
                scene_file,
                vr_video=is_vr,
                frame_interval=config.config.video_frame_interval,
                threshold=config.config.video_threshold,
                return_confidence=config.config.video_confidence_return
            )

            # Extract detected tags
            detected_tags = set()
            for category_tags in video_result.video_tags.values():
                detected_tags.update(category_tags)

            if detected_tags:
                # Add tags to scene
                tag_ids = media_handler.get_tag_ids(list(detected_tags), create=True)
                media_handler.add_tags_to_video(scene_id, tag_ids)
                log.info(f"Added tags {list(detected_tags)} to scene {scene_id}")

                # Add markers if enabled
                if config.config.create_markers:
                    media_handler.add_markers_to_video_from_dict(scene_id, video_result.tag_timespans)
                    log.info(f"Added markers to scene {scene_id}")

            # Remove VLM_TagMe tag from processed scene
            media_handler.remove_tagme_tag_from_scene(scene_id)
            
        except Exception as e:
            log.error(f"Error processing video scene {scene.get('id', 'unknown')}: {e}")
            # Add error tag to failed scene
            media_handler.add_error_scene(scene['id'])

async def __find_marker_settings(scene: Dict[str, Any]) -> None:
    """Find optimal marker settings for a scene"""
    try:
        scene_id = scene['id']
        scene_file = scene['files'][0]['path']
        
        # Get existing markers for the scene
        existing_markers = media_handler.get_scene_markers(scene_id)
        
        # Convert markers to desired timespan format
        desired_timespan_data = {}
        for marker in existing_markers:
            tag_name = marker['primary_tag']['name']
            desired_timespan_data[tag_name] = TimeFrame(
                start=marker['seconds'],
                end=marker.get('end_seconds', marker['seconds'] + 1),
                total_confidence=1.0
            )

        # Find optimal settings
        optimal_settings = await vlm_engine.find_optimal_marker_settings_async(
            existing_json={},  # No existing JSON data
            desired_timespan_data=desired_timespan_data
        )

        # Output results
        log.info(f"Optimal marker settings found for scene {scene_id}:")
        log.info(json.dumps(optimal_settings, indent=2))
        
    except Exception as e:
        log.error(f"Error finding marker settings for scene {scene.get('id', 'unknown')}: {e}")

def increment_progress() -> None:
    """Increment progress counter"""
    global progress
    progress += increment
    log.info(f"Progress: {progress:.2%}")

# ----------------- Cleanup -----------------

async def cleanup() -> None:
    """Cleanup resources"""
    if vlm_engine.vlm_engine:
        await vlm_engine.vlm_engine.shutdown()

# Run main function if script is executed directly
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Plugin interrupted by user")
    except Exception as e:
        log.error(f"Plugin failed: {e}")
        sys.exit(1)
    finally:
        asyncio.run(cleanup()) 
