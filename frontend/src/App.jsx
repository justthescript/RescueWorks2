import { useState, useEffect, useMemo } from "react";
import api, { setAuthToken } from "./api";

// Modern color palette with dark mode support
const themes = {
  light: {
    background: "#f8fafc",
    backgroundSecondary: "#ffffff",
    header: "#0f172a",
    headerGradient: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
    accent: "#3b82f6",
    accentHover: "#2563eb",
    accentGradient: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    success: "#10b981",
    warning: "#f59e0b",
    danger: "#ef4444",
    cardBorder: "#e2e8f0",
    text: "#0f172a",
    textMuted: "#64748b",
    shadow: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
    shadowLg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  },
  dark: {
    background: "#0f172a",
    backgroundSecondary: "#1e293b",
    header: "#020617",
    headerGradient: "linear-gradient(135deg, #020617 0%, #0f172a 100%)",
    accent: "#60a5fa",
    accentHover: "#3b82f6",
    accentGradient: "linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)",
    success: "#34d399",
    warning: "#fbbf24",
    danger: "#f87171",
    cardBorder: "#334155",
    text: "#f1f5f9",
    textMuted: "#94a3b8",
    shadow: "0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.3)",
    shadowLg: "0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3)",
  }
};

// Enhanced layout styles with animations
const getLayoutStyles = (colors) => ({
  page: {
    minHeight: "100vh",
    background: colors.background,
    color: colors.text,
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    transition: "all 0.3s ease",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "1rem 2rem",
    background: colors.headerGradient,
    color: "white",
    boxShadow: colors.shadowLg,
    position: "sticky",
    top: 0,
    zIndex: 100,
    backdropFilter: "blur(10px)",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    fontWeight: 700,
    fontSize: "1.25rem",
    letterSpacing: "-0.025em",
  },
  nav: {
    display: "flex",
    gap: "0.5rem",
    alignItems: "center",
  },
  navButton: (active) => ({
    padding: "0.5rem 1rem",
    borderRadius: "0.5rem",
    border: "none",
    background: active ? "rgba(255, 255, 255, 0.15)" : "transparent",
    color: "white",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: 500,
    transition: "all 0.2s ease",
    backdropFilter: "blur(10px)",
  }),
  content: {
    maxWidth: "1400px",
    margin: "2rem auto",
    padding: "0 2rem 3rem",
  },
  card: {
    border: `1px solid ${colors.cardBorder}`,
    borderRadius: "1rem",
    background: colors.backgroundSecondary,
    padding: "1.5rem",
    boxShadow: colors.shadow,
    transition: "all 0.2s ease",
  },
  button: (variant = "primary") => ({
    padding: "0.625rem 1.25rem",
    borderRadius: "0.5rem",
    border: "none",
    background: variant === "primary" ? colors.accentGradient : 
                variant === "danger" ? colors.danger : 
                variant === "success" ? colors.success : "transparent",
    color: "white",
    fontWeight: 600,
    fontSize: "0.9rem",
    cursor: "pointer",
    transition: "all 0.2s ease",
    display: "inline-flex",
    alignItems: "center",
    gap: "0.5rem",
  }),
  input: {
    width: "100%",
    padding: "0.625rem 0.875rem",
    borderRadius: "0.5rem",
    border: `1px solid ${colors.cardBorder}`,
    fontSize: "0.9rem",
    background: colors.backgroundSecondary,
    color: colors.text,
    transition: "all 0.2s ease",
  },
  badge: (status) => ({
    display: "inline-block",
    padding: "0.25rem 0.75rem",
    borderRadius: "9999px",
    fontSize: "0.75rem",
    fontWeight: 600,
    background: status === "completed" || status === "adopted" ? colors.success :
                status === "in_progress" || status === "in_foster" ? colors.warning :
                status === "pending" || status === "available" ? colors.accent :
                status === "urgent" || status === "high" ? colors.danger : colors.textMuted,
    color: "white",
  }),
  statCard: {
    background: colors.accentGradient,
    color: "white",
    padding: "1.5rem",
    borderRadius: "1rem",
    boxShadow: colors.shadowLg,
    transition: "all 0.2s ease",
  },
});

const LoadingSpinner = () => (
  <div style={{
    display: "inline-block",
    width: "20px",
    height: "20px",
    border: "3px solid rgba(255, 255, 255, 0.3)",
    borderRadius: "50%",
    borderTopColor: "white",
    animation: "spin 0.8s linear infinite",
  }}>
    <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

const SearchBar = ({ value, onChange, placeholder, colors }) => (
  <div style={{ position: "relative", maxWidth: "400px" }}>
    <span style={{
      position: "absolute",
      left: "0.875rem",
      top: "50%",
      transform: "translateY(-50%)",
      fontSize: "1.1rem",
    }}>🔍</span>
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      style={{
        width: "100%",
        padding: "0.625rem 0.875rem 0.625rem 2.5rem",
        borderRadius: "0.5rem",
        border: `1px solid ${colors.cardBorder}`,
        fontSize: "0.9rem",
        background: colors.backgroundSecondary,
        color: colors.text,
        transition: "all 0.2s ease",
      }}
    />
  </div>
);

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isDark, setIsDark] = useState(false);
  
  const colors = themes[isDark ? "dark" : "light"];
  const styles = getLayoutStyles(colors);

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const form = new FormData();
      form.append("username", email);
      form.append("password", password);
      const res = await api.post("/auth/token", form);
      const token = res.data.access_token;
      setAuthToken(token);
      onLogin(token);
    } catch (err) {
      console.error(err);
      setError("Invalid credentials. Please check your email and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={{
        position: "absolute",
        top: "1rem",
        right: "1rem",
        zIndex: 10,
      }}>
        <button
          onClick={() => setIsDark(!isDark)}
          style={{
            ...styles.button("primary"),
            background: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(10px)",
          }}
        >
          {isDark ? "☀️" : "🌙"}
        </button>
      </div>
      
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "2rem",
      }}>
        <div style={{
          width: "100%",
          maxWidth: "450px",
          ...styles.card,
          boxShadow: colors.shadowLg,
        }}>
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div style={{
              fontSize: "3rem",
              marginBottom: "1rem",
            }}>🐾</div>
            <h1 style={{
              fontSize: "1.75rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
              background: colors.accentGradient,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}>Welcome to RescueWorks</h1>
            <p style={{
              color: colors.textMuted,
              fontSize: "0.95rem",
            }}>
              Sign in to manage your rescue organization
            </p>
          </div>

          {error && (
            <div style={{
              marginBottom: "1.5rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.5rem",
              background: colors.danger,
              color: "white",
              fontSize: "0.9rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}>
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: "1rem" }}>
                <label htmlFor="email" style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                marginBottom: "0.5rem",
                color: colors.text,
              }}>
                Email Address
              </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
                style={styles.input}
                placeholder="you@example.com"
              />
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
                <label htmlFor="password" style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                marginBottom: "0.5rem",
                color: colors.text,
              }}>
                Password
              </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                style={styles.input}
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.button("primary"),
                width: "100%",
                justifyContent: "center",
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? <LoadingSpinner /> : "Sign In"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

import { getBreedsForSpecies } from "./breeds";

const [formData, setFormData] = useState({
  name: "",
  species: "",
  sex: "",
  status: "intake",

  intake_date: "",
  microchip_number: "",
  weight: "",
  altered_status: "",
  date_of_birth: "",

  description_public: "",
  description_internal: "",
  photo_url: "",
});


  const [breedInputs, setBreedInputs] = useState(["", "", ""]);
  const [openBreedIndex, setOpenBreedIndex] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    if (name === "species") {
      // When species changes, keep breed fields but close dropdown
      setOpenBreedIndex(null);
    }
  };

  const handleBreedChange = (index, value) => {
    setBreedInputs((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
    setOpenBreedIndex(index);
  };

  const handleBreedSelect = (index, value) => {
    setBreedInputs((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
    setOpenBreedIndex(null);
  };

  const breedsForCurrentSpecies = getBreedsForSpecies(formData.species);

  const getFilteredBreeds = (index) => {
    const term = breedInputs[index].toLowerCase();
    if (!breedsForCurrentSpecies.length) return [];
    if (!term) return breedsForCurrentSpecies.slice(0, 15);

    return breedsForCurrentSpecies
      .filter((b) => b.toLowerCase().includes(term))
      .slice(0, 15);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    // Combine non empty breeds into a single string
    const combinedBreed = breedInputs
      .map((b) => b.trim())
      .filter((b) => b.length > 0)
      .join(" / ");

    try {
      await api.post("/pets/", {
        ...formData,
        org_id: 1, // TODO pull from auth
        breed: combinedBreed,
      });

      setSuccess(`Successfully added ${formData.name} to intake.`);

      setFormData({
        name: "",
        species: "",
        sex: "",
        status: "intake",
        intake_date: "",
        microchip_number: "",
        weight: "",
        altered_status: "",
        date_of_birth: "",
        description_public: "",
        description_internal: "",
        photo_url: "",
      });
      setBreedInputs(["", "", ""]);
      setOpenBreedIndex(null);
    } catch (err) {
      console.error("Failed to create pet:", err);
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          const errorMessages = err.response.data.detail
            .map((e) => `${e.loc[1]}: ${e.msg}`)
            .join(", ");
          setError(errorMessages);
        } else {
          setError(err.response.data.detail);
        }
      } else {
        setError("Something went wrong while creating the pet.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.content}>
      <div style={styles.card}>
        <h1
          style={{
            fontSize: "1.75rem",
            fontWeight: 700,
            marginBottom: "0.5rem",
          }}
        >
          🐾 Animal Intake
        </h1>
        <p
          style={{
            color: colors.textMuted,
            marginBottom: "1.5rem",
            fontSize: "0.95rem",
          }}
        >
          Add new animals into your system with basic details and status.
        </p>

        {error && (
          <div
            style={{
              marginBottom: "1.5rem",
              padding: "1rem",
              borderRadius: "0.75rem",
              background:
                "linear-gradient(135deg, rgba(248, 113, 113, 0.1) 0%, rgba(239, 68, 68, 0.2) 100%)",
              border: `1px solid ${colors.danger}`,
              color: colors.danger,
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div
            style={{
              marginBottom: "1.5rem",
              padding: "1rem",
              borderRadius: "0.75rem",
              background:
                "linear-gradient(135deg, rgba(52, 211, 153, 0.1) 0%, rgba(16, 185, 129, 0.2) 100%)",
              border: `1px solid ${colors.success}`,
              color: colors.success,
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <span>✅</span>
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "1rem",
              marginBottom: "1.5rem",
            }}
          >
            {/* Name */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  marginBottom: "0.35rem",
                }}
              >
                Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                maxLength={100}
                placeholder="Enter animal name"
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  border: `1px solid ${colors.cardBorder}`,
                  background: colors.background,
                  color: colors.text,
                }}
              />
            </div>

            {/* Species */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  marginBottom: "0.35rem",
                }}
              >
                Species
              </label>
              <select
                name="species"
                value={formData.species}
                onChange={handleChange}
                required
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  border: `1px solid ${colors.cardBorder}`,
                  background: colors.background,
                  color: colors.text,
                }}
              >
                <option value="">Select</option>
                <option value="Dog">Dog</option>
                <option value="Cat">Cat</option>
                <option value="Bird">Bird</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Sex */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  marginBottom: "0.35rem",
                }}
              >
                Sex
              </label>
              <select
                name="sex"
                value={formData.sex}
                onChange={handleChange}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  border: `1px solid ${colors.cardBorder}`,
                  background: colors.background,
                  color: colors.text,
                }}
              >
                <option value="">Select</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Unknown">Unknown</option>
              </select>
            </div>

            {/* Intake Date */}
<div>
  <label
    style={{
      display: "block",
      fontSize: "0.875rem",
      fontWeight: 600,
      marginBottom: "0.35rem",
    }}
  >
    Intake Date
  </label>
  <input
    type="date"
    name="intake_date"
    value={formData.intake_date}
    onChange={handleChange}
    style={{
      width: "100%",
      padding: "0.75rem",
      borderRadius: "0.5rem",
      border: `1px solid ${colors.cardBorder}`,
      background: colors.background,
      color: colors.text,
    }}
  />
</div>

{/* Date of Birth */}
<div>
  <label
    style={{
      display: "block",
      fontSize: "0.875rem",
      fontWeight: 600,
      marginBottom: "0.35rem",
    }}
  >
    Date of Birth
  </label>
  <input
    type="date"
    name="date_of_birth"
    value={formData.date_of_birth}
    onChange={handleChange}
    style={{
      width: "100%",
      padding: "0.75rem",
      borderRadius: "0.5rem",
      border: `1px solid ${colors.cardBorder}`,
      background: colors.background,
      color: colors.text,
    }}
  />
</div>

{/* Weight */}
<div>
  <label
    style={{
      display: "block",
      fontSize: "0.875rem",
      fontWeight: 600,
      marginBottom: "0.35rem",
    }}
  >
    Weight (lbs)
  </label>
  <input
    type="number"
    name="weight"
    value={formData.weight}
    onChange={handleChange}
    step="0.1"
    min="0"
    placeholder="Enter weight"
    style={{
      width: "100%",
      padding: "0.75rem",
      borderRadius: "0.5rem",
      border: `1px solid ${colors.cardBorder}`,
      background: colors.background,
      color: colors.text,
    }}
  />
</div>

{/* Altered status */}
<div>
  <label
    style={{
      display: "block",
      fontSize: "0.875rem",
      fontWeight: 600,
      marginBottom: "0.35rem",
    }}
  >
    Altered
  </label>
  <select
    name="altered_status"
    value={formData.altered_status}
    onChange={handleChange}
    style={{
      width: "100%",
      padding: "0.75rem",
      borderRadius: "0.5rem",
      border: `1px solid ${colors.cardBorder}`,
      background: colors.background,
      color: colors.text,
    }}
  >
    <option value="">Select</option>
    <option value="yes">Yes</option>
    <option value="no">No</option>
    <option value="unsure">Unsure</option>
  </select>
</div>

{/* Microchip */}
<div>
  <label
    style={{
      display: "block",
      fontSize: "0.875rem",
      fontWeight: 600,
      marginBottom: "0.35rem",
    }}
  >
    Microchip Number
  </label>
  <input
    type="text"
    name="microchip_number"
    value={formData.microchip_number}
    onChange={handleChange}
    placeholder="Enter microchip number"
    style={{
      width: "100%",
      padding: "0.75rem",
      borderRadius: "0.5rem",
      border: `1px solid ${colors.cardBorder}`,
      background: colors.background,
      color: colors.text,
    }}
  />
</div>


            {/* Status */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  marginBottom: "0.35rem",
                }}
              >
                Status
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleChange}
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  border: `1px solid ${colors.cardBorder}`,
                  background: colors.background,
                  color: colors.text,
                }}
              >
                <option value="intake">Intake</option>
                <option value="needs_foster">Needs foster</option>
                <option value="in_foster">In foster</option>
                <option value="available">Available</option>
                <option value="adopted">Adopted</option>
              </select>
            </div>

                        {/* Photo URL and upload */}
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  marginBottom: "0.35rem",
                }}
              >
                Photo URL
              </label>
              <input
                type="url"
                name="photo_url"
                value={formData.photo_url}
                onChange={handleChange}
                placeholder="https://example.com/photo.jpg"
                style={{
                  width: "100%",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  border: `1px solid ${colors.cardBorder}`,
                  background: colors.background,
                  color: colors.text,
                }}
              />
              <ImageUploadField
                colors={colors}
                styles={styles}
                value={formData.photo_url}
                onChange={(url) =>
                  setFormData((prev) => ({ ...prev, photo_url: url }))
                }
              />
            </div>
          </div>


          {/* Breed typeahead for up to 3 breeds */}
          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{
                display: "block",
                fontSize: "0.875rem",
                fontWeight: 600,
                marginBottom: "0.35rem",
              }}
            >
              Breed
              <span style={{ fontWeight: 400, fontSize: "0.8rem", marginLeft: "0.25rem", color: colors.textMuted }}>
                up to 3 breeds, useful for mixed breeds
              </span>
            </label>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: "0.75rem",
              }}
            >
              {[0, 1, 2].map((idx) => {
                const filtered = getFilteredBreeds(idx);
                const showDropdown =
                  openBreedIndex === idx &&
                  filtered.length > 0 &&
                  formData.species &&
                  formData.species !== "Other";

                return (
                  <div
                    key={idx}
                    style={{ position: "relative", minWidth: 0 }}
                  >
                    <input
                      type="text"
                      value={breedInputs[idx]}
                      onChange={(e) =>
                        handleBreedChange(idx, e.target.value)
                      }
                      onFocus={() => {
                        if (formData.species && formData.species !== "Other") {
                          setOpenBreedIndex(idx);
                        }
                      }}
                      onBlur={() => {
                        // Small delay so click on option is registered
                        setTimeout(() => {
                          setOpenBreedIndex((current) =>
                            current === idx ? null : current
                          );
                        }, 150);
                      }}
                      placeholder={
                        formData.species && formData.species !== "Other"
                          ? "Start typing to search breeds"
                          : "Free text breed"
                      }
                      style={{
                        width: "100%",
                        padding: "0.75rem",
                        borderRadius: "0.5rem",
                        border: `1px solid ${colors.cardBorder}`,
                        background: colors.background,
                        color: colors.text,
                      }}
                    />

                    {showDropdown && (
                      <div
                        style={{
                          position: "absolute",
                          top: "100%",
                          left: 0,
                          right: 0,
                          zIndex: 10,
                          marginTop: "0.25rem",
                          maxHeight: "220px",
                          overflowY: "auto",
                          background: colors.background,
                          borderRadius: "0.5rem",
                          border: `1px solid ${colors.cardBorder}`,
                          boxShadow:
                            "0 8px 20px rgba(15, 23, 42, 0.25)",
                        }}
                      >
                        {filtered.map((b) => (
                          <button
                            key={b}
                            type="button"
                            onMouseDown={(e) => {
                              e.preventDefault();
                              handleBreedSelect(idx, b);
                            }}
                            style={{
                              width: "100%",
                              padding: "0.5rem 0.75rem",
                              textAlign: "left",
                              border: "none",
                              background: "transparent",
                              cursor: "pointer",
                              fontSize: "0.9rem",
                            }}
                          >
                            {b}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Descriptions */}
          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{
                display: "block",
                fontSize: "0.875rem",
                fontWeight: 600,
                marginBottom: "0.35rem",
              }}
            >
              Public Description
            </label>
            <textarea
              name="description_public"
              value={formData.description_public}
              onChange={handleChange}
              maxLength={2000}
              rows={3}
              placeholder="Short bio for adopters and fosters"
              style={{
                width: "100%",
                padding: "0.75rem",
                borderRadius: "0.5rem",
                border: `1px solid ${colors.cardBorder}`,
                background: colors.background,
                color: colors.text,
                resize: "vertical",
              }}
            />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{
                display: "block",
                fontSize: "0.875rem",
                fontWeight: 600,
                marginBottom: "0.35rem",
              }}
            >
              Internal Notes
            </label>
            <textarea
              name="description_internal"
              value={formData.description_internal}
              onChange={handleChange}
              maxLength={2000}
              rows={3}
              placeholder="Behavior notes, medical flags, anything staff should know"
              style={{
                width: "100%",
                padding: "0.75rem",
                borderRadius: "0.5rem",
                border: `1px solid ${colors.cardBorder}`,
                background: colors.background,
                color: colors.text,
                resize: "vertical",
              }}
            />
          </div>

          <div style={{ textAlign: "right" }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: "0.75rem 1.5rem",
                borderRadius: "999px",
                border: "none",
                cursor: loading ? "not-allowed" : "pointer",
                fontWeight: 600,
                fontSize: "0.95rem",
                background: colors.accentGradient,
                color: "white",
                boxShadow: "0 10px 25px rgba(37, 99, 235, 0.35)",
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? "Adding Animal..." : "Add to Intake"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );


function ImageUploadField({ colors, styles, value, onChange, petId }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleFileChange = (event) => {
    const selected = event.target.files && event.target.files[0];
    setFile(selected || null);
    setError("");
    setSuccess("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Select a file before uploading");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      if (petId) {
        formData.append("pet_id", String(petId));
      }
      formData.append("visibility", "internal");

      const response = await api.post("/files/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const doc = response.data;
      const path = doc.file_path || "";
      if (!path) {
        setError("Upload succeeded but no file path was returned");
      } else {
        // If uploads are served from a different base url, adjust this mapping.
        onChange(path);
        setSuccess("Image uploaded");
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Image upload failed";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ marginTop: "0.5rem" }}>
      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{
            flexGrow: 1,
            fontSize: "0.8rem",
          }}
        />
        <button
          type="button"
          onClick={handleUpload}
          disabled={uploading}
          style={{
            ...styles.button,
            padding: "0.5rem 0.75rem",
            fontSize: "0.8rem",
            opacity: uploading ? 0.7 : 1,
          }}
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>
      {value && (
        <p
          style={{
            marginTop: "0.35rem",
            fontSize: "0.75rem",
            color: colors.textMuted,
            wordBreak: "break-all",
          }}
        >
          Current: {value}
        </p>
      )}
      {error && (
        <p
          style={{
            marginTop: "0.25rem",
            fontSize: "0.75rem",
            color: colors.danger || "#ef4444",
          }}
        >
          {error}
        </p>
      )}
      {success && !error && (
        <p
          style={{
            marginTop: "0.25rem",
            fontSize: "0.75rem",
            color: colors.success || "#10b981",
          }}
        >
          {success}
        </p>
      )}
    </div>
  );
}

function PetDetailPanel({ pet, colors, styles, onClose, onPetUpdated }) {
  const [localPet, setLocalPet] = useState(pet);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [fosterIdInput, setFosterIdInput] = useState(
    pet.foster_user_id ? String(pet.foster_user_id) : ""
  );
  const [assigning, setAssigning] = useState(false);

  useEffect(() => {
    setLocalPet(pet);
    setFosterIdInput(pet.foster_user_id ? String(pet.foster_user_id) : "");
    setError("");
    setSuccess("");
  }, [pet]);

  const handleFieldChange = (event) => {
    const { name, value } = event.target;
    setLocalPet((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        name: localPet.name,
        species: localPet.species,
        breed: localPet.breed,
        sex: localPet.sex,
        status: localPet.status,
        description_public: localPet.description_public,
        description_internal: localPet.description_internal,
        photo_url: localPet.photo_url,
      };

      const response = await api.put(`/pets/${pet.id}`, payload);
      const updated = response.data;
      setLocalPet(updated);
      setSuccess("Pet updated");
      if (onPetUpdated) {
        onPetUpdated(updated);
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail || err?.message || "Unable to save pet";
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const handleAssignFoster = async () => {
    const fosterId = parseInt(fosterIdInput, 10);
    if (!fosterId) {
      setError("Enter a numeric foster user id");
      return;
    }

    setAssigning(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.post(
        `/pets/${pet.id}/assign-foster`,
        null,
        { params: { foster_user_id: fosterId } }
      );
      const updated = response.data;
      setLocalPet(updated);
      setFosterIdInput(
        updated.foster_user_id ? String(updated.foster_user_id) : ""
      );
      setSuccess("Foster assignment updated");
      if (onPetUpdated) {
        onPetUpdated(updated);
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to update foster assignment";
      setError(message);
    } finally {
      setAssigning(false);
    }
  };

  const handleClearFoster = async () => {
    setAssigning(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.delete(`/pets/${pet.id}/assign-foster`);
      const updated = response.data;
      setLocalPet(updated);
      setFosterIdInput("");
      setSuccess("Foster cleared");
      if (onPetUpdated) {
        onPetUpdated(updated);
      }
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to clear foster assignment";
      setError(message);
    } finally {
      setAssigning(false);
    }
  };

  if (!pet) {
    return null;
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 40,
        background: "rgba(15, 23, 42, 0.75)",
        display: "flex",
        justifyContent: "flex-end",
      }}
    >
      <div
        style={{
          width: "420px",
          maxWidth: "100%",
          height: "100%",
          background: colors.backgroundSecondary,
          boxShadow: styles.card.boxShadow,
          padding: "1.5rem",
          overflowY: "auto",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1rem",
          }}
        >
          <h2
            style={{
              fontSize: "1.25rem",
              fontWeight: 600,
            }}
          >
            Edit Pet: {localPet.name}
          </h2>
          <button
            type="button"
            onClick={onClose}
            style={{
              border: "none",
              background: "transparent",
              fontSize: "1.25rem",
              cursor: "pointer",
            }}
          >
            ×
          </button>
        </div>

        {error && (
          <div
            style={{
              marginBottom: "1rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.75rem",
              background: "rgba(248, 113, 113, 0.08)",
              border: `1px solid ${colors.danger || "#ef4444"}`,
              color: colors.danger || "#ef4444",
              fontSize: "0.85rem",
            }}
          >
            {error}
          </div>
        )}

        {success && !error && (
          <div
            style={{
              marginBottom: "1rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.75rem",
              background: "rgba(34, 197, 94, 0.08)",
              border: `1px solid ${colors.success || "#10b981"}`,
              color: colors.success || "#10b981",
              fontSize: "0.85rem",
            }}
          >
            {success}
          </div>
        )}

        {/* core fields */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr",
            gap: "0.75rem",
            marginBottom: "1.25rem",
          }}
        >
          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Name
            </label>
            <input
              name="name"
              value={localPet.name || ""}
              onChange={handleFieldChange}
              style={styles.input}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Species
            </label>
            <select
              name="species"
              value={localPet.species || ""}
              onChange={handleFieldChange}
              style={styles.input}
            >
              <option value="">Select</option>
              <option value="Dog">Dog</option>
              <option value="Cat">Cat</option>
              <option value="Bird">Bird</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Sex
            </label>
            <select
              name="sex"
              value={localPet.sex || ""}
              onChange={handleFieldChange}
              style={styles.input}
            >
              <option value="">Unknown</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="M">M</option>
              <option value="F">F</option>
              <option value="U">U</option>
            </select>
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Status
            </label>
            <select
              name="status"
              value={localPet.status || "intake"}
              onChange={handleFieldChange}
              style={styles.input}
            >
              <option value="intake">Intake</option>
              <option value="needs_foster">Needs Foster</option>
              <option value="in_foster">In Foster</option>
              <option value="available">Available</option>
              <option value="pending">Pending</option>
              <option value="adopted">Adopted</option>
            </select>
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Breed
            </label>
            <input
              name="breed"
              value={localPet.breed || ""}
              onChange={handleFieldChange}
              style={styles.input}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Photo URL
            </label>
            <input
              name="photo_url"
              value={localPet.photo_url || ""}
              onChange={handleFieldChange}
              style={styles.input}
            />
            <ImageUploadField
              colors={colors}
              styles={styles}
              value={localPet.photo_url || ""}
              onChange={(url) =>
                setLocalPet((prev) => ({ ...prev, photo_url: url }))
              }
              petId={pet.id}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Public Description
            </label>
            <textarea
              name="description_public"
              value={localPet.description_public || ""}
              onChange={handleFieldChange}
              rows={3}
              style={{
                ...styles.input,
                resize: "vertical",
              }}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.8rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              Internal Notes
            </label>
            <textarea
              name="description_internal"
              value={localPet.description_internal || ""}
              onChange={handleFieldChange}
              rows={3}
              style={{
                ...styles.input,
                resize: "vertical",
              }}
            />
          </div>
        </div>

        {/* foster assignment section */}
        <div
          style={{
            marginBottom: "1.5rem",
            padding: "0.75rem 1rem",
            borderRadius: "0.75rem",
            background: colors.background,
            border: `1px solid ${colors.cardBorder}`,
          }}
        >
          <h3
            style={{
              fontSize: "0.95rem",
              fontWeight: 600,
              marginBottom: "0.5rem",
            }}
          >
            Foster assignment
          </h3>
          <div
            style={{
              display: "flex",
              gap: "0.5rem",
              alignItems: "center",
              marginBottom: "0.5rem",
            }}
          >
            <input
              type="number"
              placeholder="Foster user id"
              value={fosterIdInput}
              onChange={(event) => setFosterIdInput(event.target.value)}
              style={{
                ...styles.input,
                fontSize: "0.8rem",
              }}
            />
            <button
              type="button"
              onClick={handleAssignFoster}
              disabled={assigning}
              style={{
                ...styles.button,
                fontSize: "0.8rem",
                padding: "0.5rem 0.75rem",
              }}
            >
              {assigning ? "Saving..." : "Assign"}
            </button>
            <button
              type="button"
              onClick={handleClearFoster}
              disabled={assigning}
              style={{
                ...styles.buttonSecondary,
                fontSize: "0.8rem",
                padding: "0.5rem 0.75rem",
              }}
            >
              Clear
            </button>
          </div>
          <p
            style={{
              fontSize: "0.75rem",
              color: colors.textMuted,
            }}
          >
            Current foster user id:{" "}
            {localPet.foster_user_id ? localPet.foster_user_id : "None"}
          </p>
        </div>

        {/* footer buttons */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: "0.75rem",
          }}
        >
          <button
            type="button"
            onClick={onClose}
            style={{
              ...styles.buttonSecondary,
              flex: 1,
            }}
          >
            Close
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            style={{
              ...styles.button,
              flex: 1,
              opacity: saving ? 0.8 : 1,
            }}
          >
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Dashboard({ colors, styles }) {
  const [pets, setPets] = useState([]);
  const [apps, setApps] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [donationsSummary, setDonationsSummary] = useState({
    total_donations: 0,
  });
  const [petsByStatus, setPetsByStatus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedPet, setSelectedPet] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      try {
        // Use the same endpoint as the vet portal so you actually see pets
        const [p, a, t, ds, ps] = await Promise.all([
          api.get("/vet/pets"),
          api.get("/applications"),
          api.get("/tasks"),
          api.get("/stats/donations_summary"),
          api.get("/stats/pets_by_status"),
        ]);

        if (!isMounted) return;

        setPets(p.data || []);
        setApps(a.data || []);
        setTasks(t.data || []);
        setDonationsSummary(ds.data || {});
        setPetsByStatus(ps.data || []);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredPets = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();

    return pets.filter((pet) => {
      const matchesSearch =
        !term ||
        (pet.name || "").toLowerCase().includes(term) ||
        (pet.species || "").toLowerCase().includes(term) ||
        (pet.breed || "").toLowerCase().includes(term);

      const matchesStatus =
        filterStatus === "all" || pet.status === filterStatus;

      return matchesSearch && matchesStatus;
    });
  }, [pets, searchTerm, filterStatus]);

  const stats = useMemo(() => {
    const totalDonations = Number(donationsSummary.total_donations || 0);
    const availablePets =
      petsByStatus.find((s) => s.status === "available")?.count || 0;
    const pendingApps = apps.filter(
      (a) => a.status === "submitted" || a.status === "under_review"
    ).length;
    const urgentTasks = tasks.filter(
      (t) => t.priority === "urgent" && t.status !== "completed"
    ).length;

    return { totalDonations, availablePets, pendingApps, urgentTasks };
  }, [donationsSummary, petsByStatus, apps, tasks]);

  if (loading) {
    return (
      <div
        style={{
          ...styles.content,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "60vh",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <LoadingSpinner />
          <p style={{ marginTop: "1rem", color: colors.textMuted }}>
            Loading dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.content}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "2rem",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
            }}
          >
            Dashboard
          </h1>
          <p
            style={{
              color: colors.textMuted,
              fontSize: "0.95rem",
            }}
          >
            Welcome back! Here’s what’s happening today.
          </p>
        </div>
      </div>

      {/* Stats row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1.25rem",
          marginBottom: "2rem",
        }}
      >
        <div
          style={{
            ...styles.statCard,
            background: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
          }}
        >
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🏠</div>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>
            {stats.availablePets}
          </div>
          <div style={{ fontSize: "0.875rem", opacity: 0.9 }}>
            Available for Adoption
          </div>
        </div>

        <div
          style={{
            ...styles.statCard,
            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
          }}
        >
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>💰</div>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>
            ${stats.totalDonations.toFixed(0)}
          </div>
          <div style={{ fontSize: "0.875rem", opacity: 0.9 }}>
            Total Donations
          </div>
        </div>

        <div
          style={{
            ...styles.statCard,
            background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
          }}
        >
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📋</div>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>
            {stats.pendingApps}
          </div>
          <div style={{ fontSize: "0.875rem", opacity: 0.9 }}>
            Pending Applications
          </div>
        </div>

        <div
          style={{
            ...styles.statCard,
            background: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
          }}
        >
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>⚠️</div>
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>
            {stats.urgentTasks}
          </div>
          <div style={{ fontSize: "0.875rem", opacity: 0.9 }}>
            Urgent Tasks
          </div>
        </div>
      </div>

      {/* Pets preview card */}
      <div style={{ ...styles.card, marginBottom: "2rem" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.5rem",
          }}
        >
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600 }}>
            🐾 Pets ({filteredPets.length})
          </h2>
          <div
            style={{ display: "flex", gap: "1rem", alignItems: "center" }}
          >
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Search pets..."
              colors={colors}
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                ...styles.input,
                width: "auto",
                minWidth: "140px",
              }}
            >
              <option value="all">All Status</option>
              <option value="intake">Intake</option>
              <option value="needs_foster">Needs Foster</option>
              <option value="in_foster">In Foster</option>
              <option value="available">Available</option>
              <option value="pending">Pending</option>
              <option value="adopted">Adopted</option>
            </select>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: "1rem",
          }}
        >
          {filteredPets.slice(0, 6).map((pet) => (
            <div
              key={pet.id}
              onClick={() => setSelectedPet(pet)}
              style={{
                ...styles.card,
                padding: "1rem",
                cursor: "pointer",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = colors.shadowLg;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = colors.shadow;
              }}
            >
              {pet.photo_url && (
                <img
                  src={pet.photo_url}
                  alt={pet.name}
                  style={{
                    width: "100%",
                    height: "180px",
                    objectFit: "cover",
                    borderRadius: "0.75rem",
                    marginBottom: "0.75rem",
                  }}
                />
              )}
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 600,
                  marginBottom: "0.25rem",
                }}
              >
                {pet.name}
              </h3>
              <p
                style={{
                  fontSize: "0.875rem",
                  color: colors.textMuted,
                  marginBottom: "0.5rem",
                }}
              >
                {pet.species} • {pet.breed || "Mixed"}
              </p>
              <span style={styles.badge(pet.status)}>
                {pet.status.replace("_", " ").toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Applications and tasks */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 2fr) minmax(0, 1.5fr)",
          gap: "1.5rem",
        }}
      >
        <div style={styles.card}>
          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 600,
              marginBottom: "1rem",
            }}
          >
            📝 Recent Applications
          </h3>
          <div
            style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}
          >
            {apps.slice(0, 5).map((app) => (
              <div
                key={app.id}
                style={{
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  background: colors.background,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div
                    style={{ fontWeight: 500, fontSize: "0.9rem" }}
                  >
                    {app.type} Application
                  </div>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: colors.textMuted,
                    }}
                  >
                    {app.applicant_name || "Applicant"}
                  </div>
                </div>
                <span style={styles.badge(app.status)}>
                  {app.status.replace("_", " ")}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div style={styles.card}>
          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 600,
              marginBottom: "1rem",
            }}
          >
            ✅ Tasks
          </h3>
          <div
            style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}
          >
            {tasks.slice(0, 5).map((task) => (
              <div
                key={task.id}
                style={{
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  background: colors.background,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div style={{ flex: 1 }}>
                  <div
                    style={{ fontWeight: 500, fontSize: "0.9rem" }}
                  >
                    {task.title}
                  </div>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: colors.textMuted,
                    }}
                  >
                    Due: {task.due_date || "No due date"}
                  </div>
                </div>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <span style={styles.badge(task.priority)}>
                    {task.priority}
                  </span>
                  <span style={styles.badge(task.status)}>
                    {task.status.replace("_", " ")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedPet && (
        <PetDetailPanel
          pet={selectedPet}
          colors={colors}
          styles={styles}
          onClose={() => setSelectedPet(null)}
          onPetUpdated={(updated) => {
            setPets((prev) =>
              prev.map((p) => (p.id === updated.id ? updated : p))
            );
            setSelectedPet(updated);
          }}
        />
      )}
    </div>
  );
}

function PetsPage({ colors, styles }) {
  const [pets, setPets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [selectedPet, setSelectedPet] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadPets() {
      try {
        const res = await api.get("/vet/pets");
        if (!isMounted) return;
        setPets(res.data || []);
      } catch (err) {
        console.error("Failed to load pets", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadPets();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredPets = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    return pets.filter((pet) => {
      const matchesSearch =
        !term ||
        (pet.name || "").toLowerCase().includes(term) ||
        (pet.species || "").toLowerCase().includes(term) ||
        (pet.breed || "").toLowerCase().includes(term);

      const matchesStatus =
        filterStatus === "all" || pet.status === filterStatus;

      return matchesSearch && matchesStatus;
    });
  }, [pets, searchTerm, filterStatus]);

  if (loading) {
    return (
      <div
        style={{
          ...styles.content,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "60vh",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <LoadingSpinner />
          <p style={{ marginTop: "1rem", color: colors.textMuted }}>
            Loading pets...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.content}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
            }}
          >
            All Pets
          </h1>
          <p
            style={{
              color: colors.textMuted,
              fontSize: "0.95rem",
            }}
          >
            Search and edit pets in bulk. Click any card to edit details or
            assign a foster.
          </p>
        </div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <SearchBar
            value={searchTerm}
            onChange={setSearchTerm}
            placeholder="Search pets..."
            colors={colors}
          />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            style={{
              ...styles.input,
              width: "auto",
              minWidth: "160px",
            }}
          >
            <option value="all">All Status</option>
            <option value="intake">Intake</option>
            <option value="needs_foster">Needs Foster</option>
            <option value="in_foster">In Foster</option>
            <option value="available">Available</option>
            <option value="pending">Pending</option>
            <option value="adopted">Adopted</option>
          </select>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: "1rem",
        }}
      >
        {filteredPets.map((pet) => (
          <div
            key={pet.id}
            onClick={() => setSelectedPet(pet)}
            style={{
              ...styles.card,
              padding: "1rem",
              cursor: "pointer",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-4px)";
              e.currentTarget.style.boxShadow = colors.shadowLg;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = colors.shadow;
            }}
          >
            {pet.photo_url && (
              <img
                src={pet.photo_url}
                alt={pet.name}
                style={{
                  width: "100%",
                  height: "180px",
                  objectFit: "cover",
                  borderRadius: "0.75rem",
                  marginBottom: "0.75rem",
                }}
              />
            )}
            <h3
              style={{
                fontSize: "1.1rem",
                fontWeight: 600,
                marginBottom: "0.25rem",
              }}
            >
              {pet.name}
            </h3>
            <p
              style={{
                fontSize: "0.875rem",
                color: colors.textMuted,
                marginBottom: "0.35rem",
              }}
            >
              {pet.species} • {pet.breed || "Mixed"}
            </p>
            <p
              style={{
                fontSize: "0.8rem",
                color: colors.textMuted,
                marginBottom: "0.5rem",
              }}
            >
              Status:{" "}
              <span style={styles.badge(pet.status)}>
                {pet.status.replace("_", " ").toUpperCase()}
              </span>
            </p>
          </div>
        ))}
      </div>

      {selectedPet && (
        <PetDetailPanel
          pet={selectedPet}
          colors={colors}
          styles={styles}
          onClose={() => setSelectedPet(null)}
          onPetUpdated={(updated) => {
            setPets((prev) =>
              prev.map((p) => (p.id === updated.id ? updated : p))
            );
            setSelectedPet(updated);
          }}
        />
      )}
    </div>
  );
}




function SettingsPage({ colors, styles }) {
  const [org, setOrg] = useState({ name: "", logo_url: "", primary_contact_email: "" });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/settings");
        setOrg(res.data.organization);
      } catch (err) {
        console.error("Failed to load settings", err);
      }
    }
    load();
  }, []);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await api.put("/settings", { organization: org });
      setMessage("Settings saved successfully! ✅");
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      console.error("Failed to save settings", err);
      setMessage("Failed to save settings. ❌");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={styles.content}>
      <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        ⚙️ Settings
      </h1>
      <p style={{ color: colors.textMuted, marginBottom: "2rem", fontSize: "0.95rem" }}>
        Manage your organization profile and preferences
      </p>

      <div style={{ maxWidth: "600px" }}>
        <div style={styles.card}>
          {message && (
            <div style={{
              marginBottom: "1.5rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.5rem",
              background: message.includes("✅") ? colors.success : colors.danger,
              color: "white",
              fontSize: "0.9rem",
            }}>
              {message}
            </div>
          )}

          <form onSubmit={handleSave}>
            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{
                display: "block",
                fontSize: "0.875rem",
                fontWeight: 600,
                marginBottom: "0.5rem",
              }}>
                Organization Name
              </label>
              <input
                type="text"
                value={org.name}
                onChange={(e) => setOrg({ ...org, name: e.target.value })}
                style={styles.input}
                placeholder="Paws & Claws Rescue"
              />
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{
                display: "block",
                fontSize: "0.875rem",
                fontWeight: 600,
                marginBottom: "0.5rem",
              }}>
                Logo URL
              </label>
              <input
                type="url"
                value={org.logo_url}
                onChange={(e) => setOrg({ ...org, logo_url: e.target.value })}
                style={styles.input}
                placeholder="https://example.com/logo.png"
              />
            </div>

            <div style={{ marginBottom: "2rem" }}>
              <label style={{
                display: "block",
                fontSize: "0.875rem",
                fontWeight: 600,
                marginBottom: "0.5rem",
              }}>
                Primary Contact Email
              </label>
              <input
                type="email"
                value={org.primary_contact_email}
                onChange={(e) => setOrg({ ...org, primary_contact_email: e.target.value })}
                style={styles.input}
                placeholder="contact@rescue.org"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              style={{
                ...styles.button("primary"),
                opacity: saving ? 0.7 : 1,
              }}
            >
              {saving ? <LoadingSpinner /> : "Save Settings"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function MyPortal({ colors, styles }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/portal/me");
        setSummary(res.data);
      } catch (err) {
        console.error("Failed to load portal", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div style={{
        ...styles.content,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "60vh",
      }}>
        <div style={{ textAlign: "center" }}>
          <LoadingSpinner />
          <p style={{ marginTop: "1rem", color: colors.textMuted }}>Loading your portal...</p>
        </div>
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div style={styles.content}>
      <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "0.5rem" }}>
        👤 My Portal
      </h1>
      <p style={{ color: colors.textMuted, marginBottom: "2rem", fontSize: "0.95rem" }}>
        Your personal dashboard for applications, foster pets, and tasks
      </p>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
        gap: "1.5rem",
      }}>
        <div style={styles.card}>
          <h3 style={{
            fontSize: "1.1rem",
            fontWeight: 600,
            marginBottom: "1rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}>
            📝 My Applications
            <span style={{
              ...styles.badge(),
              marginLeft: "auto",
            }}>
              {summary.my_applications.length}
            </span>
          </h3>
          {summary.my_applications.length === 0 ? (
            <p style={{ fontSize: "0.9rem", color: colors.textMuted }}>
              No applications yet.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {summary.my_applications.map((a) => (
                <div
                  key={a.id}
                  style={{
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    background: colors.background,
                  }}
                >
                  <div style={{ fontWeight: 500 }}>{a.type}</div>
                  <span style={styles.badge(a.status)}>{a.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={styles.card}>
          <h3 style={{
            fontSize: "1.1rem",
            fontWeight: 600,
            marginBottom: "1rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}>
            🏠 My Foster Pets
            <span style={{
              ...styles.badge(),
              marginLeft: "auto",
            }}>
              {summary.my_foster_pets.length}
            </span>
          </h3>
          {summary.my_foster_pets.length === 0 ? (
            <p style={{ fontSize: "0.9rem", color: colors.textMuted }}>
              No foster pets assigned.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {summary.my_foster_pets.map((p) => (
                <div
                  key={p.id}
                  style={{
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    background: colors.background,
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                  }}
                >
                  <div style={{
                    width: "50px",
                    height: "50px",
                    borderRadius: "0.5rem",
                    background: colors.accentGradient,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.5rem",
                  }}>
                    🐾
                  </div>
                  <div>
                    <div style={{ fontWeight: 500 }}>{p.name}</div>
                    <div style={{ fontSize: "0.85rem", color: colors.textMuted }}>
                      {p.species}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={styles.card}>
          <h3 style={{
            fontSize: "1.1rem",
            fontWeight: 600,
            marginBottom: "1rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}>
            ✅ My Tasks
            <span style={{
              ...styles.badge(),
              marginLeft: "auto",
            }}>
              {summary.my_tasks.length}
            </span>
          </h3>
          {summary.my_tasks.length === 0 ? (
            <p style={{ fontSize: "0.9rem", color: colors.textMuted }}>
              No tasks assigned.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {summary.my_tasks.map((t) => (
                <div
                  key={t.id}
                  style={{
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    background: colors.background,
                  }}
                >
                  <div style={{ fontWeight: 500, marginBottom: "0.25rem" }}>
                    {t.title}
                  </div>
                  <span style={styles.badge(t.status)}>{t.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function VetPortal({ colors, styles }) {
  const [pets, setPets] = useState([]);
  const [selectedPet, setSelectedPet] = useState(null);
  const [medical, setMedical] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const [editPet, setEditPet] = useState(null);
  const [savingPet, setSavingPet] = useState(false);
  const [petError, setPetError] = useState("");
  const [petMessage, setPetMessage] = useState("");

  useEffect(() => {
    async function loadPets() {
      try {
        const res = await api.get("/vet/pets");
        setPets(res.data);
      } catch (err) {
        console.error("Failed to load vet pets", err);
      } finally {
        setLoading(false);
      }
    }
    loadPets();
  }, []);

  const filteredPets = useMemo(() => {
    return pets.filter((pet) => {
      const search = searchTerm.toLowerCase();
      return (
        pet.name.toLowerCase().includes(search) ||
        (pet.species || "").toLowerCase().includes(search) ||
        (pet.breed || "").toLowerCase().includes(search)
      );
    });
  }, [pets, searchTerm]);

  async function selectPet(pet) {
    setSelectedPet(pet);
    setMedical([]);
    setPetError("");
    setPetMessage("");

    // seed edit state from the selected pet
    setEditPet({
      name: pet.name || "",
      species: pet.species || "",
      breed: pet.breed || "",
      sex: pet.sex || "",
      status: pet.status || "intake",
      description_public: pet.description_public || "",
      description_internal: pet.description_internal || "",
      photo_url: pet.photo_url || "",
      foster_user_id: pet.foster_user_id || "",
      adopter_user_id: pet.adopter_user_id || "",
    });

    try {
      const res = await api.get(`/vet/pets/${pet.id}/medical`);
      setMedical(res.data);
    } catch (err) {
      console.error("Failed to load medical", err);
    }
  }

  const handleEditChange = (e) => {
    if (!editPet) return;
    const { name, value } = e.target;
    setEditPet((prev) => ({ ...prev, [name]: value }));
  };

  const handleSavePet = async (e) => {
    e.preventDefault();
    if (!selectedPet || !editPet) return;

    setSavingPet(true);
    setPetError("");
    setPetMessage("");

    try {
      const payload = {
        ...editPet,
        foster_user_id: editPet.foster_user_id
          ? Number(editPet.foster_user_id)
          : null,
        adopter_user_id: editPet.adopter_user_id
          ? Number(editPet.adopter_user_id)
          : null,
      };

      const res = await api.put(`/pets/${selectedPet.id}`, payload);

      // update local lists and selected pet
      setPets((prev) =>
        prev.map((p) => (p.id === res.data.id ? res.data : p))
      );
      setSelectedPet(res.data);
      setEditPet((prev) => ({
        ...prev,
        status: res.data.status,
        foster_user_id: res.data.foster_user_id || "",
        adopter_user_id: res.data.adopter_user_id || "",
      }));
      setPetMessage("Pet details updated.");
    } catch (err) {
      console.error("Failed to update pet", err);
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          const msgs = err.response.data.detail
            .map((e) => `${e.loc[1]}: ${e.msg}`)
            .join(", ");
          setPetError(msgs);
        } else {
          setPetError(err.response.data.detail);
        }
      } else {
        setPetError("Something went wrong while updating the pet.");
      }
    } finally {
      setSavingPet(false);
    }
  };

  const renderCurrentLocation = () => {
    if (!selectedPet) return "";
    if (selectedPet.status === "adopted" && selectedPet.adopter_user_id) {
      return `Adopted (user id ${selectedPet.adopter_user_id})`;
    }
    if (selectedPet.status === "in_foster" && selectedPet.foster_user_id) {
      return `In foster (user id ${selectedPet.foster_user_id})`;
    }
    if (selectedPet.status === "needs_foster") {
      return "Needs foster placement";
    }
    return "Shelter or unassigned";
  };

  if (loading) {
    return (
      <div
        style={{
          ...styles.content,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "60vh",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <LoadingSpinner />
          <p style={{ marginTop: "1rem", color: colors.textMuted }}>
            Loading vet portal...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.content}>
      <h1
        style={{
          fontSize: "2rem",
          fontWeight: 700,
          marginBottom: "0.5rem",
        }}
      >
        🏥 Veterinary Portal
      </h1>
      <p
        style={{
          color: colors.textMuted,
          marginBottom: "2rem",
          fontSize: "0.95rem",
        }}
      >
        Manage medical records and update key details for your animals.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "350px 1fr",
          gap: "1.5rem",
        }}
      >
        {/* Left side list of pets */}
        <div style={styles.card}>
          <div style={{ marginBottom: "1rem" }}>
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Search by name, species, or breed"
              colors={colors}
            />
          </div>

          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 600,
              marginBottom: "1rem",
            }}
          >
            Patients ({filteredPets.length})
          </h3>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "0.5rem",
              maxHeight: "600px",
              overflowY: "auto",
            }}
          >
            {filteredPets.map((p) => (
              <button
                key={p.id}
                onClick={() => selectPet(p)}
                style={{
                  ...styles.card,
                  padding: "0.75rem",
                  cursor: "pointer",
                  background:
                    selectedPet && selectedPet.id === p.id
                      ? colors.accentGradient
                      : colors.background,
                  color:
                    selectedPet && selectedPet.id === p.id
                      ? "white"
                      : colors.text,
                  border: "none",
                  textAlign: "left",
                  transition: "all 0.2s ease",
                }}
              >
                <div style={{ fontWeight: 500 }}>{p.name}</div>
                <div
                  style={{
                    fontSize: "0.85rem",
                    opacity: 0.8,
                  }}
                >
                  {p.species} • {p.breed || "Mixed"}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right side detail and edit panel */}
        <div style={styles.card}>
          {selectedPet ? (
            <>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "1rem",
                  marginBottom: "1.5rem",
                  paddingBottom: "1.5rem",
                  borderBottom: `1px solid ${colors.cardBorder}`,
                }}
              >
                {selectedPet.photo_url && (
                  <img
                    src={selectedPet.photo_url}
                    alt={selectedPet.name}
                    style={{
                      width: "100px",
                      height: "100px",
                      objectFit: "cover",
                      borderRadius: "0.75rem",
                    }}
                  />
                )}
                <div>
                  <h2
                    style={{
                      fontSize: "1.5rem",
                      fontWeight: 700,
                      marginBottom: "0.25rem",
                    }}
                  >
                    {selectedPet.name}
                  </h2>
                  <p style={{ color: colors.textMuted }}>
                    {selectedPet.species} • {selectedPet.breed || "Mixed"}
                  </p>
                  <div style={{ marginTop: "0.4rem" }}>
                    <span style={styles.badge(selectedPet.status)}>
                      {selectedPet.status.replace("_", " ").toUpperCase()}
                    </span>
                  </div>
                  <p
                    style={{
                      marginTop: "0.5rem",
                      fontSize: "0.85rem",
                      color: colors.textMuted,
                    }}
                  >
                    Current location: {renderCurrentLocation()}
                  </p>
                </div>
              </div>

              {/* Edit pet details */}
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 600,
                  marginBottom: "0.75rem",
                }}
              >
                Edit Details
              </h3>

              {petError && (
                <div
                  style={{
                    marginBottom: "0.75rem",
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    border: `1px solid ${colors.danger}`,
                    background:
                      "linear-gradient(135deg, rgba(248,113,113,0.08), rgba(239,68,68,0.14))",
                    color: colors.danger,
                    fontSize: "0.9rem",
                  }}
                >
                  {petError}
                </div>
              )}

              {petMessage && (
                <div
                  style={{
                    marginBottom: "0.75rem",
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    border: `1px solid ${colors.success}`,
                    background:
                      "linear-gradient(135deg, rgba(52,211,153,0.08), rgba(16,185,129,0.14))",
                    color: colors.success,
                    fontSize: "0.9rem",
                  }}
                >
                  {petMessage}
                </div>
              )}

              {editPet && (
                <form
                  onSubmit={handleSavePet}
                  style={{ marginBottom: "1.5rem" }}
                >
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "repeat(auto-fit, minmax(180px, 1fr))",
                      gap: "0.75rem 1rem",
                      marginBottom: "1rem",
                    }}
                  >
                    {/* Name */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Name
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={editPet.name}
                        onChange={handleEditChange}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      />
                    </div>

                    {/* Species */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Species
                      </label>
                      <input
                        type="text"
                        name="species"
                        value={editPet.species}
                        onChange={handleEditChange}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      />
                    </div>

                    {/* Breed */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Breed
                      </label>
                      <input
                        type="text"
                        name="breed"
                        value={editPet.breed}
                        onChange={handleEditChange}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      />
                    </div>

                    {/* Sex */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Sex
                      </label>
                      <select
                        name="sex"
                        value={editPet.sex || ""}
                        onChange={handleEditChange}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      >
                        <option value="">Unset</option>
                        <option value="Female">Female</option>
                        <option value="Male">Male</option>
                        <option value="Unknown">Unknown</option>
                      </select>
                    </div>

                    {/* Status */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Status
                      </label>
                      <select
                        name="status"
                        value={editPet.status}
                        onChange={handleEditChange}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      >
                        <option value="intake">Intake</option>
                        <option value="needs_foster">Needs foster</option>
                        <option value="in_foster">In foster</option>
                        <option value="available">Available</option>
                        <option value="adopted">Adopted</option>
                      </select>
                    </div>

                    {/* Foster user id */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Foster user id
                      </label>
                      <input
                        type="number"
                        name="foster_user_id"
                        value={editPet.foster_user_id}
                        onChange={handleEditChange}
                        placeholder="Numeric user id"
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      />
                    </div>

                    {/* Adopter user id */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Adopter user id
                      </label>
                      <input
                        type="number"
                        name="adopter_user_id"
                        value={editPet.adopter_user_id}
                        onChange={handleEditChange}
                        placeholder="Numeric user id"
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      />
                    </div>

                    {/* Photo URL */}
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          marginBottom: "0.25rem",
                        }}
                      >
                        Photo URL
                      </label>
                      <input
                        type="url"
                        name="photo_url"
                        value={editPet.photo_url}
                        onChange={handleEditChange}
                        style={{
                          width: "100%",
                          padding: "0.6rem",
                          borderRadius: "0.4rem",
                          border: `1px solid ${colors.cardBorder}`,
                          background: colors.background,
                          color: colors.text,
                        }}
                      />
                    </div>
                  </div>

                  {/* Descriptions */}
                  <div style={{ marginBottom: "0.75rem" }}>
                    <label
                      style={{
                        display: "block",
                        fontSize: "0.8rem",
                        fontWeight: 600,
                        marginBottom: "0.25rem",
                      }}
                    >
                      Public description
                    </label>
                    <textarea
                      name="description_public"
                      value={editPet.description_public}
                      onChange={handleEditChange}
                      rows={3}
                      style={{
                        width: "100%",
                        padding: "0.6rem",
                        borderRadius: "0.4rem",
                        border: `1px solid ${colors.cardBorder}`,
                        background: colors.background,
                        color: colors.text,
                        resize: "vertical",
                        fontSize: "0.9rem",
                      }}
                    />
                  </div>

                  <div style={{ marginBottom: "0.75rem" }}>
                    <label
                      style={{
                        display: "block",
                        fontSize: "0.8rem",
                        fontWeight: 600,
                        marginBottom: "0.25rem",
                      }}
                    >
                      Internal notes
                    </label>
                    <textarea
                      name="description_internal"
                      value={editPet.description_internal}
                      onChange={handleEditChange}
                      rows={3}
                      style={{
                        width: "100%",
                        padding: "0.6rem",
                        borderRadius: "0.4rem",
                        border: `1px solid ${colors.cardBorder}`,
                        background: colors.background,
                        color: colors.text,
                        resize: "vertical",
                        fontSize: "0.9rem",
                      }}
                    />
                  </div>

                  <div style={{ textAlign: "right", marginTop: "0.5rem" }}>
                    <button
                      type="submit"
                      disabled={savingPet}
                      style={{
                        padding: "0.6rem 1.4rem",
                        borderRadius: "999px",
                        border: "none",
                        cursor: savingPet ? "not-allowed" : "pointer",
                        fontWeight: 600,
                        fontSize: "0.9rem",
                        background: colors.accentGradient,
                        color: "white",
                        boxShadow:
                          "0 8px 20px rgba(37, 99, 235, 0.35)",
                        opacity: savingPet ? 0.75 : 1,
                      }}
                    >
                      {savingPet ? "Saving..." : "Save changes"}
                    </button>
                  </div>
                </form>
              )}

              {/* Medical records list, same as before */}
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 600,
                  marginBottom: "1rem",
                }}
              >
                📋 Medical Records
              </h3>

              {medical.length === 0 ? (
                <div
                  style={{
                    textAlign: "center",
                    padding: "3rem 1rem",
                    color: colors.textMuted,
                  }}
                >
                  <div
                    style={{ fontSize: "3rem", marginBottom: "1rem" }}
                  >
                    📋
                  </div>
                  <p>No medical records yet.</p>
                </div>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "1rem",
                  }}
                >
                  {medical.map((m) => (
                    <div
                      key={m.id}
                      style={{
                        padding: "1rem",
                        borderRadius: "0.5rem",
                        background: colors.background,
                        border: `1px solid ${colors.cardBorder}`,
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "start",
                          marginBottom: "0.5rem",
                        }}
                      >
                        <div style={{ fontWeight: 600 }}>
                          {m.description || m.note || "Medical Record"}
                        </div>
                        <div
                          style={{
                            fontSize: "0.8rem",
                            color: colors.textMuted,
                          }}
                        >
                          {new Date(
                            m.created_at
                          ).toLocaleDateString()}
                        </div>
                      </div>
                      {m.note && (
                        <p
                          style={{
                            fontSize: "0.9rem",
                            color: colors.textMuted,
                            marginTop: "0.5rem",
                          }}
                        >
                          {m.note}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div
              style={{
                textAlign: "center",
                padding: "4rem 1rem",
                color: colors.textMuted,
              }}
            >
              <div
                style={{ fontSize: "3rem", marginBottom: "1rem" }}
              >
                🐾
              </div>
              <p>Select a patient from the left to view and edit details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


// ============================================================================
// FOSTER COORDINATOR COMPONENTS
// ============================================================================

function FosterCoordinatorDashboard({ colors, styles }) {
  const [stats, setStats] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsRes, matchesRes] = await Promise.all([
          api.get("/foster-coordinator/dashboard/stats"),
          api.get("/foster-coordinator/matches/suggest"),
        ]);
        setStats(statsRes.data);
        setMatches(matchesRes.data || []);
      } catch (err) {
        console.error("Failed to load foster coordinator data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div style={{ ...styles.content, textAlign: "center", padding: "3rem" }}>
        <LoadingSpinner />
        <p style={{ marginTop: "1rem", color: colors.textMuted }}>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div style={styles.content}>
      <h1 style={{ fontSize: "2rem", marginBottom: "2rem", fontWeight: 700 }}>
        🏡 Foster Coordinator Dashboard
      </h1>

      {/* Stats Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
        gap: "1.5rem",
        marginBottom: "2rem",
      }}>
        <div style={styles.statCard}>
          <div style={{ fontSize: "0.875rem", opacity: 0.9, marginBottom: "0.5rem" }}>
            Active Fosters
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: 700 }}>
            {stats?.total_active_fosters || 0}
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={{ fontSize: "0.875rem", opacity: 0.9, marginBottom: "0.5rem" }}>
            Available Fosters
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: 700 }}>
            {stats?.total_available_fosters || 0}
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={{ fontSize: "0.875rem", opacity: 0.9, marginBottom: "0.5rem" }}>
            Pets Needing Foster
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: 700 }}>
            {stats?.pets_needing_foster || 0}
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={{ fontSize: "0.875rem", opacity: 0.9, marginBottom: "0.5rem" }}>
            Pets In Foster
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: 700 }}>
            {stats?.pets_in_foster || 0}
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={{ fontSize: "0.875rem", opacity: 0.9, marginBottom: "0.5rem" }}>
            Available Capacity
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: 700 }}>
            {stats?.available_foster_capacity || 0}
          </div>
        </div>

        <div style={styles.statCard}>
          <div style={{ fontSize: "0.875rem", opacity: 0.9, marginBottom: "0.5rem" }}>
            Avg. Placement Days
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: 700 }}>
            {stats?.avg_placement_duration_days?.toFixed(0) || "N/A"}
          </div>
        </div>
      </div>

      {/* Suggested Matches */}
      <div style={{ ...styles.card, marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", fontWeight: 600 }}>
          🎯 Suggested Matches
        </h2>

        {matches.length === 0 ? (
          <p style={{ color: colors.textMuted, textAlign: "center", padding: "2rem" }}>
            No matches available at this time
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {matches.slice(0, 10).map((match, idx) => (
              <div
                key={idx}
                style={{
                  padding: "1rem",
                  border: `1px solid ${colors.cardBorder}`,
                  borderRadius: "0.5rem",
                  background: colors.background,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, marginBottom: "0.5rem" }}>
                      {match.pet_name} ({match.pet_species}) → {match.foster_name}
                    </div>
                    <div style={{ fontSize: "0.875rem", color: colors.textMuted, marginBottom: "0.5rem" }}>
                      {match.foster_email}
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                      {match.match_reasons.map((reason, i) => (
                        <span
                          key={i}
                          style={{
                            fontSize: "0.75rem",
                            padding: "0.25rem 0.5rem",
                            background: colors.accent,
                            color: "white",
                            borderRadius: "0.25rem",
                          }}
                        >
                          {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div style={{
                    marginLeft: "1rem",
                    textAlign: "right",
                  }}>
                    <div style={{
                      fontSize: "1.5rem",
                      fontWeight: 700,
                      color: colors.accent,
                    }}>
                      {match.match_score.toFixed(0)}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: colors.textMuted }}>
                      score
                    </div>
                    <div style={{ fontSize: "0.75rem", color: colors.textMuted, marginTop: "0.25rem" }}>
                      Load: {match.current_foster_load}/{match.max_capacity}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Placements */}
      <div style={styles.card}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", fontWeight: 600 }}>
          📋 Recent Placements
        </h2>

        {!stats?.recent_placements || stats.recent_placements.length === 0 ? (
          <p style={{ color: colors.textMuted, textAlign: "center", padding: "2rem" }}>
            No recent placements
          </p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: `2px solid ${colors.cardBorder}` }}>
                  <th style={{ padding: "0.75rem", textAlign: "left" }}>Pet ID</th>
                  <th style={{ padding: "0.75rem", textAlign: "left" }}>Start Date</th>
                  <th style={{ padding: "0.75rem", textAlign: "left" }}>Outcome</th>
                  <th style={{ padding: "0.75rem", textAlign: "left" }}>Agreement</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_placements.map((placement) => (
                  <tr key={placement.id} style={{ borderBottom: `1px solid ${colors.cardBorder}` }}>
                    <td style={{ padding: "0.75rem" }}>{placement.pet_id}</td>
                    <td style={{ padding: "0.75rem" }}>
                      {new Date(placement.start_date).toLocaleDateString()}
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span style={styles.badge(placement.outcome)}>
                        {placement.outcome}
                      </span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      {placement.agreement_signed ? "✅" : "⏳"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function FosterProfileManagement({ colors, styles }) {
  const [profiles, setProfiles] = useState([]);
  const [myProfile, setMyProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingProfile, setEditingProfile] = useState(null);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    loadProfiles();
  }, []);

  async function loadProfiles() {
    try {
      const [profilesRes, myProfileRes] = await Promise.all([
        api.get("/foster-coordinator/profiles"),
        api.get("/foster-coordinator/profiles/me").catch(() => ({ data: null })),
      ]);
      setProfiles(profilesRes.data || []);
      setMyProfile(myProfileRes.data);
    } catch (err) {
      console.error("Failed to load profiles:", err);
    } finally {
      setLoading(false);
    }
  }

  async function createOrUpdateProfile() {
    try {
      if (myProfile) {
        // Update existing profile
        await api.patch("/foster-coordinator/profiles/me", formData);
      } else {
        // Create new profile
        await api.post("/foster-coordinator/profiles", {
          ...formData,
          org_id: 1, // TODO: Get from user context
        });
      }
      await loadProfiles();
      setEditingProfile(null);
      setFormData({});
    } catch (err) {
      console.error("Failed to save profile:", err);
      alert("Failed to save profile");
    }
  }

  if (loading) {
    return (
      <div style={{ ...styles.content, textAlign: "center", padding: "3rem" }}>
        <LoadingSpinner />
        <p style={{ marginTop: "1rem", color: colors.textMuted }}>Loading profiles...</p>
      </div>
    );
  }

  return (
    <div style={styles.content}>
      <h1 style={{ fontSize: "2rem", marginBottom: "2rem", fontWeight: 700 }}>
        👥 Foster Profile Management
      </h1>

      {/* My Profile Section */}
      <div style={{ ...styles.card, marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", fontWeight: 600 }}>
          My Foster Profile
        </h2>

        {!myProfile && !editingProfile ? (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <p style={{ color: colors.textMuted, marginBottom: "1rem" }}>
              You don't have a foster profile yet
            </p>
            <button
              onClick={() => setEditingProfile(true)}
              style={styles.button("primary")}
            >
              Create Profile
            </button>
          </div>
        ) : editingProfile ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>
                Experience Level
              </label>
              <select
                value={formData.experience_level || "none"}
                onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                style={styles.input}
              >
                <option value="none">None</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>
                Preferred Species (comma-separated)
              </label>
              <input
                type="text"
                value={formData.preferred_species || ""}
                onChange={(e) => setFormData({ ...formData, preferred_species: e.target.value })}
                style={styles.input}
                placeholder="e.g., dog, cat"
              />
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>
                Max Capacity
              </label>
              <input
                type="number"
                value={formData.max_capacity || 1}
                onChange={(e) => setFormData({ ...formData, max_capacity: parseInt(e.target.value) })}
                style={styles.input}
                min="1"
              />
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>
                Home Type
              </label>
              <select
                value={formData.home_type || ""}
                onChange={(e) => setFormData({ ...formData, home_type: e.target.value })}
                style={styles.input}
              >
                <option value="">Select...</option>
                <option value="house">House</option>
                <option value="apartment">Apartment</option>
                <option value="condo">Condo</option>
                <option value="townhouse">Townhouse</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={formData.has_yard || false}
                  onChange={(e) => setFormData({ ...formData, has_yard: e.target.checked })}
                />
                Has Yard
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={formData.can_handle_medical || false}
                  onChange={(e) => setFormData({ ...formData, can_handle_medical: e.target.checked })}
                />
                Can Handle Medical
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={formData.can_handle_behavioral || false}
                  onChange={(e) => setFormData({ ...formData, can_handle_behavioral: e.target.checked })}
                />
                Can Handle Behavioral
              </label>
            </div>

            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
              <button onClick={createOrUpdateProfile} style={styles.button("primary")}>
                Save Profile
              </button>
              <button
                onClick={() => {
                  setEditingProfile(null);
                  setFormData({});
                }}
                style={styles.button("secondary")}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "1rem", marginBottom: "1rem" }}>
              <div>
                <strong>Experience:</strong> {myProfile.experience_level}
              </div>
              <div>
                <strong>Capacity:</strong> {myProfile.current_capacity}/{myProfile.max_capacity}
              </div>
              <div>
                <strong>Home Type:</strong> {myProfile.home_type || "N/A"}
              </div>
              <div>
                <strong>Total Fosters:</strong> {myProfile.total_fosters}
              </div>
              <div>
                <strong>Successful Adoptions:</strong> {myProfile.successful_adoptions}
              </div>
              <div>
                <strong>Rating:</strong> {myProfile.rating ? `${myProfile.rating}⭐` : "N/A"}
              </div>
            </div>
            <button
              onClick={() => {
                setEditingProfile(true);
                setFormData(myProfile);
              }}
              style={styles.button("primary")}
            >
              Edit Profile
            </button>
          </div>
        )}
      </div>

      {/* All Profiles */}
      <div style={styles.card}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "1.5rem", fontWeight: 600 }}>
          All Foster Profiles ({profiles.length})
        </h2>

        <div style={{ display: "grid", gap: "1rem" }}>
          {profiles.map((profile) => (
            <div
              key={profile.id}
              style={{
                padding: "1rem",
                border: `1px solid ${colors.cardBorder}`,
                borderRadius: "0.5rem",
                background: colors.background,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: "0.5rem" }}>
                    Foster Profile #{profile.id}
                  </div>
                  <div style={{ fontSize: "0.875rem", color: colors.textMuted }}>
                    Experience: {profile.experience_level} | Capacity: {profile.current_capacity}/{profile.max_capacity}
                  </div>
                  {profile.preferred_species && (
                    <div style={{ fontSize: "0.875rem", color: colors.textMuted }}>
                      Prefers: {profile.preferred_species}
                    </div>
                  )}
                </div>
                <div style={{ textAlign: "right" }}>
                  {profile.rating && (
                    <div style={{ fontWeight: 600, color: colors.accent }}>
                      {profile.rating}⭐
                    </div>
                  )}
                  <div style={{ fontSize: "0.75rem", color: colors.textMuted }}>
                    {profile.total_fosters} total fosters
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(null);
  const [view, setView] = useState("dashboard");
  const [isDark, setIsDark] = useState(false);

  const colors = themes[isDark ? "dark" : "light"];
  const styles = getLayoutStyles(colors);

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div style={styles.logo}>
          <span role="img" aria-label="paw">🐾</span>
          <span>RescueWorks</span>
        </div>
        <nav style={styles.nav}>
          <button
  style={styles.navButton(view === "dashboard")}
  onClick={() => setView("dashboard")}
  onMouseEnter={(e) => {
    if (view !== "dashboard") {
      e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
    }
  }}
  onMouseLeave={(e) => {
    if (view !== "dashboard") {
      e.currentTarget.style.background = "transparent";
    }
  }}
>
  🏠 Dashboard
</button>

<button
  style={styles.navButton(view === "pets")}
  onClick={() => setView("pets")}
  onMouseEnter={(e) => {
    if (view !== "pets") {
      e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
    }
  }}
  onMouseLeave={(e) => {
    if (view !== "pets") {
      e.currentTarget.style.background = "transparent";
    }
  }}
>
  🐾 Pets
</button>

<button
  style={styles.navButton(view === "intake")}
  onClick={() => setView("intake")}
  onMouseEnter={(e) => {
    if (view !== "intake") {
      e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
    }
  }}
  onMouseLeave={(e) => {
    if (view !== "intake") {
      e.currentTarget.style.background = "transparent";
    }
  }}
>
  📝 Intake
          </button>
          <button
            style={styles.navButton(view === "my")}
            onClick={() => setView("my")}
            onMouseEnter={(e) => {
              if (view !== "my") {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (view !== "my") {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            👤 My Portal
          </button>
          <button
            style={styles.navButton(view === "vet")}
            onClick={() => setView("vet")}
            onMouseEnter={(e) => {
              if (view !== "vet") {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (view !== "vet") {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            🏥 Vet Portal
          </button>
          <button
            style={styles.navButton(view === "foster")}
            onClick={() => setView("foster")}
            onMouseEnter={(e) => {
              if (view !== "foster") {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (view !== "foster") {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            🏡 Foster Coordinator
          </button>
          <button
            style={styles.navButton(view === "foster-profiles")}
            onClick={() => setView("foster-profiles")}
            onMouseEnter={(e) => {
              if (view !== "foster-profiles") {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (view !== "foster-profiles") {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            👥 Foster Profiles
          </button>
          <button
            style={styles.navButton(view === "settings")}
            onClick={() => setView("settings")}
            onMouseEnter={(e) => {
              if (view !== "settings") {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (view !== "settings") {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            ⚙️ Settings
          </button>
          <button
            onClick={() => setIsDark(!isDark)}
            style={{
              ...styles.navButton(false),
              marginLeft: "0.5rem",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
            }}
          >
            {isDark ? "☀️" : "🌙"}
          </button>
        </nav>
      </header>
      {view === "dashboard" && <Dashboard colors={colors} styles={styles} />}
      {view === "pets" && <PetsPage colors={colors} styles={styles} />}
      {view === "intake" && <AnimalIntakeForm colors={colors} styles={styles} />}
      {view === "settings" && <SettingsPage colors={colors} styles={styles} />}
      {view === "my" && <MyPortal colors={colors} styles={styles} />}
      {view === "vet" && <VetPortal colors={colors} styles={styles} />}
      {view === "foster" && <FosterCoordinatorDashboard colors={colors} styles={styles} />}
      {view === "foster-profiles" && <FosterProfileManagement colors={colors} styles={styles} />}
    </div>
  );
}
