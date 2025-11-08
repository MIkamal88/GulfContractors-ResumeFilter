"""
Job profiles manager with file-based persistence.
Stores custom profiles in a JSON file without needing a database.
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
from models import JobProfile
from job_profiles_data import DEFAULT_JOB_PROFILES


class JobProfilesManager:
    """Manages job profiles with file-based persistence."""

    def __init__(self, storage_file: str = "custom_profiles.json"):
        """
        Initialize the profiles manager.

        Args:
            storage_file: Path to the JSON file for storing custom profiles
        """
        self.storage_file = Path(storage_file)
        self.default_profiles = DEFAULT_JOB_PROFILES
        self._load_custom_profiles()

    def _load_custom_profiles(self) -> None:
        """Load custom profiles from the JSON file."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.custom_profiles: Dict[str, JobProfile] = {
                        profile_id: JobProfile(**profile_data)
                        for profile_id, profile_data in data.items()
                    }
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading custom profiles: {e}")
                self.custom_profiles = {}
        else:
            self.custom_profiles = {}

    def _save_custom_profiles(self) -> None:
        """Save custom profiles to the JSON file."""
        try:
            # Convert JobProfile objects to dictionaries
            data = {
                profile_id: profile.model_dump()
                for profile_id, profile in self.custom_profiles.items()
            }

            # Ensure the directory exists
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)

            # Write to file with pretty formatting
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving custom profiles: {e}")
            raise

    def get_all_profiles(self) -> List[JobProfile]:
        """Get all available profiles (default + custom)."""
        return self.default_profiles + list(self.custom_profiles.values())

    def get_profile_by_id(self, profile_id: str) -> Optional[JobProfile]:
        """
        Get a specific profile by ID.

        Args:
            profile_id: The ID of the profile to retrieve

        Returns:
            JobProfile if found, None otherwise
        """
        # Check default profiles
        for profile in self.default_profiles:
            if profile.id == profile_id:
                return profile

        # Check custom profiles
        return self.custom_profiles.get(profile_id)

    def add_custom_profile(self, profile: JobProfile) -> JobProfile:
        """
        Add a custom profile and save to file.

        Args:
            profile: The JobProfile to add

        Returns:
            The added JobProfile

        Raises:
            ValueError: If profile ID conflicts with a default profile
        """
        # Check if ID conflicts with default profiles
        for default_profile in self.default_profiles:
            if default_profile.id == profile.id:
                raise ValueError(
                    f"Profile ID '{profile.id}' conflicts with a default profile. "
                    "Please use a different ID."
                )

        # Add to custom profiles
        self.custom_profiles[profile.id] = profile

        # Save to file
        self._save_custom_profiles()

        return profile

    def update_custom_profile(
        self, profile_id: str, profile: JobProfile
    ) -> Optional[JobProfile]:
        """
        Update an existing custom profile.

        Args:
            profile_id: The ID of the profile to update
            profile: The updated JobProfile

        Returns:
            The updated JobProfile if successful, None if profile doesn't exist

        Raises:
            ValueError: If trying to update a default profile
        """
        # Cannot update default profiles
        for default_profile in self.default_profiles:
            if default_profile.id == profile_id:
                raise ValueError("Cannot update default job profiles")

        # Check if custom profile exists
        if profile_id not in self.custom_profiles:
            return None

        # Update profile
        self.custom_profiles[profile_id] = profile

        # Save to file
        self._save_custom_profiles()

        return profile

    def delete_custom_profile(self, profile_id: str) -> bool:
        """
        Delete a custom profile.

        Args:
            profile_id: The ID of the profile to delete

        Returns:
            True if deleted successfully, False if profile doesn't exist

        Raises:
            ValueError: If trying to delete a default profile
        """
        # Cannot delete default profiles
        for default_profile in self.default_profiles:
            if default_profile.id == profile_id:
                raise ValueError("Cannot delete default job profiles")

        # Check if custom profile exists
        if profile_id not in self.custom_profiles:
            return False

        # Delete profile
        del self.custom_profiles[profile_id]

        # Save to file
        self._save_custom_profiles()

        return True

    def get_profiles_by_category(self, category: str) -> List[JobProfile]:
        """
        Get all profiles in a specific category.

        Args:
            category: The category to filter by

        Returns:
            List of JobProfiles in the category
        """
        all_profiles = self.get_all_profiles()
        return [p for p in all_profiles if p.category.lower() == category.lower()]

    def get_categories(self) -> List[str]:
        """
        Get all unique categories.

        Returns:
            Sorted list of category names
        """
        all_profiles = self.get_all_profiles()
        categories = set(p.category for p in all_profiles)
        return sorted(list(categories))

    def is_default_profile(self, profile_id: str) -> bool:
        """
        Check if a profile is a default (built-in) profile.

        Args:
            profile_id: The ID of the profile to check

        Returns:
            True if it's a default profile, False otherwise
        """
        return any(p.id == profile_id for p in self.default_profiles)

    def get_profile_stats(self) -> Dict[str, int]:
        """
        Get statistics about profiles.

        Returns:
            Dictionary with profile counts
        """
        return {
            "total": len(self.get_all_profiles()),
            "default": len(self.default_profiles),
            "custom": len(self.custom_profiles),
            "categories": len(self.get_categories()),
        }
