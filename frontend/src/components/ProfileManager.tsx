import React, { useState, useEffect } from "react";
import type { JobProfile } from "../types";
import {
  getJobProfiles,
  createCustomProfile,
  updateCustomProfile,
  deleteCustomProfile,
} from "../services/api";

interface ProfileManagerProps {
  onClose: () => void;
  onProfileCreated?: () => void;
}

const ProfileManager: React.FC<ProfileManagerProps> = ({
  onClose,
  onProfileCreated,
}) => {
  const [profiles, setProfiles] = useState<JobProfile[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state
  const [isEditing, setIsEditing] = useState(false);
  const [editingProfileId, setEditingProfileId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "",
    keywords: [] as string[],
  });
  const [keywordInput, setKeywordInput] = useState("");

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    setLoading(true);
    try {
      const data = await getJobProfiles();
      setProfiles(data.profiles);
      setCategories(data.categories);
    } catch {
      setError("Failed to load profiles");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      category: "",
      keywords: [],
    });
    setKeywordInput("");
    setIsEditing(false);
    setEditingProfileId(null);
    setError(null);
    setSuccess(null);
  };

  const handleAddKeyword = () => {
    if (keywordInput.trim()) {
      const newKeywords = keywordInput
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k.length > 0 && !formData.keywords.includes(k));

      if (newKeywords.length > 0) {
        setFormData({
          ...formData,
          keywords: [...formData.keywords, ...newKeywords],
        });
      }
      setKeywordInput("");
    }
  };

  const handleRemoveKeyword = (index: number) => {
    setFormData({
      ...formData,
      keywords: formData.keywords.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = async (e?: React.FormEvent | React.MouseEvent) => {
    if (e) {
      e.preventDefault();
    }
    setError(null);
    setSuccess(null);

    // Validation
    if (!formData.name || !formData.category) {
      setError("Please fill in all required fields");
      return;
    }

    if (formData.keywords.length === 0) {
      setError("Please add at least one keyword");
      return;
    }

    setLoading(true);

    try {
      const profile: JobProfile = {
        id: isEditing && editingProfileId 
          ? editingProfileId 
          : `profile_${Date.now()}`,
        name: formData.name,
        description: formData.description,
        category: formData.category,
        keywords: formData.keywords,
      };

      if (isEditing && editingProfileId) {
        await updateCustomProfile(editingProfileId, profile);
        setSuccess("Profile updated successfully!");
      } else {
        await createCustomProfile(profile);
        setSuccess("Profile created successfully!");
      }

      await loadProfiles();

      // Don't reset form immediately - let user see success message
      setTimeout(() => {
        resetForm();
      }, 1500);

      if (onProfileCreated) {
        onProfileCreated();
      }
    } catch (err) {
      const errorMessage =
        (err as { response?: { data?: { detail?: string } }; message?: string })
          .response?.data?.detail ||
        (err as { message?: string }).message ||
        "Failed to save profile";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (profile: JobProfile) => {
    setFormData({
      name: profile.name,
      description: profile.description,
      category: profile.category,
      keywords: [...profile.keywords],
    });
    setIsEditing(true);
    setEditingProfileId(profile.id);
    setError(null);
    setSuccess(null);
  };

  const handleDelete = async (profileId: string) => {
    if (!window.confirm("Are you sure you want to delete this profile?")) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await deleteCustomProfile(profileId);
      setSuccess("Profile deleted successfully!");
      await loadProfiles();

      if (onProfileCreated) {
        onProfileCreated();
      }
    } catch (err) {
      setError(
        (err as { response?: { data?: { detail?: string } }; message?: string })
          .response?.data?.detail ||
          (err as { message?: string }).message ||
          "Failed to delete profile",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDuplicate = async (profile: JobProfile) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const duplicatedProfile: JobProfile = {
        id: `profile_${Date.now()}`,
        name: `${profile.name} (Copy)`,
        description: profile.description,
        category: profile.category,
        keywords: [...profile.keywords],
      };

      await createCustomProfile(duplicatedProfile);
      setSuccess("Profile duplicated successfully!");
      await loadProfiles();

      if (onProfileCreated) {
        onProfileCreated();
      }
    } catch (err) {
      const errorMessage =
        (err as { response?: { data?: { detail?: string } }; message?: string })
          .response?.data?.detail ||
        (err as { message?: string }).message ||
        "Failed to duplicate profile";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // All profiles are custom profiles now
  const customProfiles = profiles;

  return (
    <div
      className="profile-manager-overlay"
      onClick={(e) => {
        // Close only if clicking the overlay, not the modal
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="profile-manager-modal">
        <div className="profile-manager-header">
          <h2>Manage Job Profiles</h2>
          <button
            type="button"
            className="close-btn"
            onClick={(e) => {
              e.preventDefault();
              onClose();
            }}
            aria-label="Close"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="profile-manager-content">
          {/* Error/Success Messages */}
          {error && (
            <div className="message-box error-box">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="message-box success-box">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span>{success}</span>
            </div>
          )}

          {/* Create/Edit Form */}
          <div className="profile-form-section">
            <h3>{isEditing ? "Edit Profile" : "Create New Profile"}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="profile-name">
                    Profile Name <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="profile-name"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    placeholder="e.g., Senior Backend Engineer"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="profile-category">
                    Category <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="profile-category"
                    value={formData.category}
                    onChange={(e) =>
                      setFormData({ ...formData, category: e.target.value })
                    }
                    placeholder="e.g., Technology"
                    list="category-suggestions"
                    required
                  />
                  <datalist id="category-suggestions">
                    {categories.map((cat) => (
                      <option key={cat} value={cat} />
                    ))}
                  </datalist>
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="profile-description">Description</label>
                <textarea
                  id="profile-description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Brief description of this job profile"
                  rows={2}
                />
              </div>

              <div className="form-field">
                <label htmlFor="profile-keywords">
                  Keywords <span className="required">*</span>
                </label>
                <div className="keyword-input-group">
                  <input
                    type="text"
                    id="profile-keywords"
                    value={keywordInput}
                    onChange={(e) => setKeywordInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleAddKeyword();
                      }
                    }}
                    placeholder="Enter keywords (comma-separated)"
                  />
                  <button
                    type="button"
                    onClick={handleAddKeyword}
                    className="add-keyword-btn"
                  >
                    Add
                  </button>
                </div>

                <div className="keywords-display">
                  {formData.keywords.map((keyword, index) => (
                    <span key={index} className="keyword-tag">
                      {keyword}
                      <button
                        type="button"
                        onClick={() => handleRemoveKeyword(index)}
                        className="keyword-remove"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <small>{formData.keywords.length} keywords added</small>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="submit-btn"
                  disabled={loading}
                  onClick={handleSubmit}
                >
                  {loading
                    ? "Saving..."
                    : isEditing
                      ? "Update Profile"
                      : "Create Profile"}
                </button>
                {isEditing && (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="cancel-btn"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Custom Profiles List */}
          <div className="custom-profiles-section">
            <h3>Your Custom Profiles ({customProfiles.length})</h3>

            {customProfiles.length === 0 ? (
              <p className="empty-message">
                No custom profiles yet. Create one above!
              </p>
            ) : (
              <div className="profiles-list">
                {customProfiles.map((profile) => (
                  <div key={profile.id} className="profile-card">
                    <div className="profile-card-header">
                      <div>
                        <h4>{profile.name}</h4>
                        <span className="profile-category">
                          {profile.category}
                        </span>
                      </div>
                      <div className="profile-actions">
                        <button
                          type="button"
                          onClick={() => handleDuplicate(profile)}
                          className="duplicate-btn"
                          title="Duplicate profile"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                          </svg>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleEdit(profile)}
                          className="edit-btn"
                          title="Edit profile"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(profile.id)}
                          className="delete-btn"
                          title="Delete profile"
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            <line x1="10" y1="11" x2="10" y2="17"/>
                            <line x1="14" y1="11" x2="14" y2="17"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                    <p className="profile-description">{profile.description}</p>
                    <p className="profile-keywords-count">
                      {profile.keywords.length} keywords
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileManager;
