"""
Video Matcher Service
Matches text/speech to sign language videos
Refactored from isl_player.py
"""

import os
from pathlib import Path
from typing import Optional, List, Dict


class VideoMatcher:
    """Match text to sign language videos"""
    
    def __init__(self, videos_path):
        """
        Initialize video matcher
        
        Args:
            videos_path: Path to sign language videos directory
        """
        self.videos_path = Path(videos_path)
        self.available_videos = self._scan_videos()
        print(f"✅ Video matcher initialized with {len(self.available_videos)} videos")
    
    def _scan_videos(self) -> Dict[str, str]:
        """Scan videos directory and create mapping"""
        videos = {}
        
        if not self.videos_path.exists():
            print(f"⚠️  Videos directory not found: {self.videos_path}")
            return videos
        
        try:
            for file in self.videos_path.iterdir():
                if file.suffix.lower() == '.mp4':
                    normalized_name = self.normalize_name(file.name)
                    videos[normalized_name] = file.name
                    print(f"   📹 {file.name}")
        except Exception as e:
            print(f"⚠️  Error scanning videos: {e}")
        
        return videos
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize string for comparison"""
        name = name.lower()
        if name.endswith('.mp4'):
            name = name[:-4]
        return name.replace('_', ' ').strip()
    
    def find_video(self, text: str) -> Optional[Dict[str, str]]:
        """Find matching video for given text"""
        if not text:
            return None
        
        normalized_text = self.normalize_name(text)
        
        # Exact match
        if normalized_text in self.available_videos:
            filename = self.available_videos[normalized_text]
            return {
                'filename': filename,
                'normalized_name': normalized_text,
                'match_type': 'exact'
            }
        
        # Partial match
        for video_name, filename in self.available_videos.items():
            if video_name in normalized_text or normalized_text in video_name:
                return {
                    'filename': filename,
                    'normalized_name': video_name,
                    'match_type': 'partial'
                }
        
        return None
    
    def get_all_videos(self) -> List[Dict[str, str]]:
        """Get list of all available videos"""
        videos = []
        for normalized_name, filename in sorted(self.available_videos.items()):
            videos.append({
                'name': normalized_name.title(),
                'filename': filename,
                'normalized_name': normalized_name
            })
        return videos
    
    def get_video_path(self, filename: str) -> Optional[str]:
        """Get full path to video file"""
        path = self.videos_path / filename
        return str(path) if path.exists() else None
