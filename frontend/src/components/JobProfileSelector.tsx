import React, { useEffect, useState, useCallback } from "react";
import type { JobProfile } from "../types";
import { getJobProfiles } from "../services/api";
import ProfileManager from "./ProfileManager";

interface JobProfileSelectorProps {
  onProfileSelect: (keywords: string[]) => void;
  onError?: (error: string) => void;
}

const JobProfileSelector: React.FC<JobProfileSelectorProps> = ({
  onProfileSelect,
  onError,
}) => {
  const [profiles, setProfiles] = useState<JobProfile[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedProfile, setSelectedProfile] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [showManager, setShowManager] = useState(false);

  const loadProfiles = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getJobProfiles();
      setProfiles(data.profiles);
      setCategories(data.categories);
    } catch {
      const errorMessage = "Failed to load job profiles";
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => {
    loadProfiles();
  }, [loadProfiles]);

  const filteredProfiles =
    selectedCategory === "all"
      ? profiles
      : profiles.filter((p) => p.category === selectedCategory);

  const handleProfileChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const profileId = e.target.value;
    setSelectedProfile(profileId);

    if (profileId) {
      const profile = profiles.find((p) => p.id === profileId);
      if (profile) {
        onProfileSelect(profile.keywords);
      }
    }
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCategory(e.target.value);
    setSelectedProfile("");
  };

  if (loading) {
    return (
      <div className="job-profile-selector">
        <label>Job Profile Template</label>
        <div className="loading-message">Loading job profiles...</div>
      </div>
    );
  }

  return (
    <div className="job-profile-selector">
      <label htmlFor="job-profile-category">Job Profile Template</label>
      <div className="profile-selectors">
        <select
          id="job-profile-category"
          value={selectedCategory}
          onChange={handleCategoryChange}
          className="category-select"
        >
          <option value="all">All Categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>

        <select
          id="job-profile"
          value={selectedProfile}
          onChange={handleProfileChange}
          className="profile-select"
          disabled={filteredProfiles.length === 0}
        >
          <option value="">Select a job profile...</option>
          {filteredProfiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name} ({profile.keywords.length} keywords)
            </option>
          ))}
        </select>
      </div>

      {selectedProfile && (
        <div className="profile-info">
          <p className="profile-description">
            {profiles.find((p) => p.id === selectedProfile)?.description}
          </p>
          <p className="profile-note">
            Keywords have been loaded. You can add or remove keywords as needed.
          </p>
        </div>
      )}

      <button
        type="button"
        onClick={() => setShowManager(true)}
        className="manage-profiles-btn"
      >
        ⚙️ Manage Custom Profiles
      </button>

      {showManager && (
        <ProfileManager
          onClose={() => setShowManager(false)}
          onProfileCreated={() => {
            loadProfiles();
            setSelectedProfile("");
          }}
        />
      )}
    </div>
  );
};

export default JobProfileSelector;
