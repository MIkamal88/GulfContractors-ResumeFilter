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
    id: "",
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
      id: "",
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
    if (!formData.id || !formData.name || !formData.category) {
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
        id: formData.id,
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
      id: profile.id,
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
          >
            ✕
          </button>
        </div>

        <div className="profile-manager-content">
          {/* Error/Success Messages */}
          {error && (
            <div className="message-box error-box">
              <span>⚠️ {error}</span>
            </div>
          )}

          {success && (
            <div className="message-box success-box">
              <span>✓ {success}</span>
            </div>
          )}

          {/* Create/Edit Form */}
          <div className="profile-form-section">
            <h3>{isEditing ? "Edit Profile" : "Create New Profile"}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="profile-id">
                    Profile ID <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="profile-id"
                    value={formData.id}
                    onChange={(e) =>
                      setFormData({ ...formData, id: e.target.value })
                    }
                    placeholder="e.g., my_custom_profile"
                    disabled={isEditing}
                    required
                  />
                  <small>
                    Use lowercase with underscores (cannot be changed after
                    creation)
                  </small>
                </div>

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
                          onClick={() => handleEdit(profile)}
                          className="edit-btn"
                          title="Edit profile"
                        >
                          ✎
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(profile.id)}
                          className="delete-btn"
                          title="Delete profile"
                        >
                          🗑
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
