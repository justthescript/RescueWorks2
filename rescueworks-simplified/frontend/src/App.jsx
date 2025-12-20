import { useState, useEffect } from 'react';
import * as api from './utils/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await api.getCurrentUser();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCurrentPage('dashboard');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <AuthPage onLogin={setUser} />;
  }

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-content">
          <h1>🐾 RescueWorks</h1>
          <div className="nav-menu">
            <button className={currentPage === 'dashboard' ? 'active' : ''} onClick={() => setCurrentPage('dashboard')}>
              Dashboard
            </button>
            <button className={currentPage === 'animals' ? 'active' : ''} onClick={() => setCurrentPage('animals')}>
              Animals
            </button>
            <button className={currentPage === 'foster' ? 'active' : ''} onClick={() => setCurrentPage('foster')}>
              Foster Management
            </button>
            <button className={currentPage === 'operations' ? 'active' : ''} onClick={() => setCurrentPage('operations')}>
              Operations
            </button>
            {(user.role === 'admin' || user.role === 'coordinator') && (
              <button className={currentPage === 'admin' ? 'active' : ''} onClick={() => setCurrentPage('admin')}>
                Admin
              </button>
            )}
            <button onClick={logout}>Logout ({user.full_name})</button>
          </div>
        </div>
      </nav>

      <div className="container">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'animals' && <AnimalsPage />}
        {currentPage === 'foster' && <FosterPage user={user} />}
        {currentPage === 'operations' && <OperationsPage />}
        {currentPage === 'admin' && <AdminPage />}
      </div>
    </div>
  );
}

// AUTH PAGE
function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (isLogin) {
        const response = await api.login({
          username: formData.email,
          password: formData.password
        });
        localStorage.setItem('token', response.data.access_token);
        onLogin(response.data.user);
      } else {
        await api.register(formData);
        const loginResponse = await api.login({
          username: formData.email,
          password: formData.password
        });
        localStorage.setItem('token', loginResponse.data.access_token);
        onLogin(loginResponse.data.user);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isLogin ? 'Login' : 'Register'}</h2>
        {error && <div className="error">{error}</div>}
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
              </div>
            </>
          )}
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{width: '100%', marginBottom: '1rem'}}>
            {isLogin ? 'Login' : 'Register'}
          </button>
        </form>
        <p style={{textAlign: 'center', color: '#666'}}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            style={{background: 'none', border: 'none', color: '#667eea', cursor: 'pointer', textDecoration: 'underline'}}
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
}

// DASHBOARD (Sprint 3)
function Dashboard() {
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, summaryRes] = await Promise.all([
        api.getFosterDashboard(),
        api.getDashboardSummary()
      ]);
      setStats(statsRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    }
  };

  if (!stats || !summary) return <div className="loading">Loading dashboard...</div>;

  return (
    <>
      <h2 style={{marginBottom: '1.5rem', color: '#333'}}>Operations Dashboard</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_animals}</div>
          <div className="stat-label">Total Animals</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.animals_in_intake}</div>
          <div className="stat-label">In Intake</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.animals_needs_foster}</div>
          <div className="stat-label">Needs Foster</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.animals_in_foster}</div>
          <div className="stat-label">In Foster</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.animals_available}</div>
          <div className="stat-label">Available</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.animals_adopted}</div>
          <div className="stat-label">Adopted</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.active_fosters}</div>
          <div className="stat-label">Active Fosters</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.available_foster_capacity}</div>
          <div className="stat-label">Foster Capacity</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>Last 30 Days</h3>
          <p>New Intakes: <strong>{summary.last_30_days.new_intakes}</strong></p>
          <p>New Placements: <strong>{summary.last_30_days.new_placements}</strong></p>
          <p>New Adoptions: <strong>{summary.last_30_days.new_adoptions}</strong></p>
        </div>

        <div className="card">
          <h3>Current Status</h3>
          <p>Active Placements: <strong>{summary.current.active_placements}</strong></p>
          <p>Animals Needing Foster: <strong>{summary.current.animals_needing_foster}</strong></p>
        </div>
      </div>

      {stats.recent_intakes.length > 0 && (
        <div className="card">
          <h3>Recent Intakes</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Species</th>
                  <th>Breed</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_intakes.map((animal) => (
                  <tr key={animal.id}>
                    <td>{animal.name}</td>
                    <td>{animal.species}</td>
                    <td>{animal.breed || 'Unknown'}</td>
                    <td><span className={`badge badge-${animal.status}`}>{animal.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}

// ANIMALS PAGE (Sprint 1)
function AnimalsPage() {
  const [animals, setAnimals] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    species: 'Dog',
    breed: '',
    age_years: '',
    sex: 'Male',
    weight: '',
    color: '',
    medical_notes: '',
    behavioral_notes: '',
    description: ''
  });
  const [photoFile, setPhotoFile] = useState(null);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadAnimals();
  }, []);

  const loadAnimals = async () => {
    try {
      const response = await api.getAnimals();
      setAnimals(response.data);
    } catch (error) {
      console.error('Failed to load animals:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.createAnimal({
        ...formData,
        age_years: parseInt(formData.age_years) || null,
        weight: parseFloat(formData.weight) || null
      });

      if (photoFile) {
        await api.uploadAnimalPhoto(response.data.id, photoFile);
      }

      setSuccess('Animal intake created successfully!');
      setShowForm(false);
      setFormData({
        name: '',
        species: 'Dog',
        breed: '',
        age_years: '',
        sex: 'Male',
        weight: '',
        color: '',
        medical_notes: '',
        behavioral_notes: '',
        description: ''
      });
      setPhotoFile(null);
      loadAnimals();
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      alert('Failed to create animal intake');
    }
  };

  return (
    <>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
        <h2>Animal Management</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ New Intake'}
        </button>
      </div>

      {success && <div className="success">{success}</div>}

      {showForm && (
        <div className="card">
          <h3>Animal Intake Form</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Species *</label>
                <select
                  value={formData.species}
                  onChange={(e) => setFormData({...formData, species: e.target.value})}
                  required
                >
                  <option value="Dog">Dog</option>
                  <option value="Cat">Cat</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Breed</label>
                <input
                  type="text"
                  value={formData.breed}
                  onChange={(e) => setFormData({...formData, breed: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Age (years)</label>
                <input
                  type="number"
                  value={formData.age_years}
                  onChange={(e) => setFormData({...formData, age_years: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Sex</label>
                <select
                  value={formData.sex}
                  onChange={(e) => setFormData({...formData, sex: e.target.value})}
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>

              <div className="form-group">
                <label>Weight (lbs)</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.weight}
                  onChange={(e) => setFormData({...formData, weight: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Color</label>
                <input
                  type="text"
                  value={formData.color}
                  onChange={(e) => setFormData({...formData, color: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setPhotoFile(e.target.files[0])}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Medical Notes</label>
              <textarea
                value={formData.medical_notes}
                onChange={(e) => setFormData({...formData, medical_notes: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Behavioral Notes</label>
              <textarea
                value={formData.behavioral_notes}
                onChange={(e) => setFormData({...formData, behavioral_notes: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </div>

            <button type="submit" className="btn btn-primary">Create Intake</button>
          </form>
        </div>
      )}

      <div className="grid grid-3">
        {animals.map((animal) => (
          <div key={animal.id} className="animal-card">
            <div className="animal-card-image">
              {animal.photo_url ? (
                <img src={animal.photo_url} alt={animal.name} />
              ) : (
                <span>No Photo</span>
              )}
            </div>
            <div className="animal-card-content">
              <h3>{animal.name}</h3>
              <p><strong>{animal.species}</strong> - {animal.breed || 'Unknown'}</p>
              <p>{animal.age_years ? `${animal.age_years} years` : 'Age unknown'} • {animal.sex || 'Unknown'}</p>
              <p><span className={`badge badge-${animal.status}`}>{animal.status}</span></p>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

// FOSTER PAGE (Sprint 2)
function FosterPage({ user }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [matches, setMatches] = useState([]);
  const [profile, setProfile] = useState(null);
  const [placements, setPlacements] = useState([]);
  const [showProfileForm, setShowProfileForm] = useState(false);

  useEffect(() => {
    if (activeTab === 'dashboard') {
      loadMatches();
    } else if (activeTab === 'profile') {
      loadProfile();
    } else if (activeTab === 'placements') {
      loadPlacements();
    }
  }, [activeTab]);

  const loadMatches = async () => {
    try {
      const response = await api.getSuggestedMatches();
      setMatches(response.data);
    } catch (error) {
      console.error('Failed to load matches:', error);
    }
  };

  const loadProfile = async () => {
    try {
      const response = await api.getMyFosterProfile();
      setProfile(response.data);
      setShowProfileForm(false);
    } catch (error) {
      if (error.response?.status === 404) {
        setShowProfileForm(true);
      }
    }
  };

  const loadPlacements = async () => {
    try {
      const response = await api.getPlacements();
      setPlacements(response.data);
    } catch (error) {
      console.error('Failed to load placements:', error);
    }
  };

  const handleCreatePlacement = async (match) => {
    if (!confirm(`Create placement for ${match.animal_name} with ${match.foster_name}?`)) return;

    try {
      await api.createPlacement({
        animal_id: match.animal_id,
        foster_profile_id: match.foster_profile_id
      });
      alert('Placement created successfully!');
      loadMatches();
    } catch (error) {
      alert('Failed to create placement');
    }
  };

  return (
    <>
      <h2 style={{marginBottom: '1.5rem'}}>Foster Management</h2>

      <div style={{marginBottom: '1.5rem'}}>
        <button
          className={`btn ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('dashboard')}
          style={{marginRight: '0.5rem'}}
        >
          Matching Dashboard
        </button>
        <button
          className={`btn ${activeTab === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('profile')}
          style={{marginRight: '0.5rem'}}
        >
          My Foster Profile
        </button>
        <button
          className={`btn ${activeTab === 'placements' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('placements')}
        >
          Placements
        </button>
      </div>

      {activeTab === 'dashboard' && (
        <div>
          <h3>Suggested Matches</h3>
          {matches.length === 0 ? (
            <p>No matches found</p>
          ) : (
            <div className="grid grid-2">
              {matches.slice(0, 10).map((match, idx) => (
                <div key={idx} className="match-card">
                  <div className="match-score">Match Score: {match.score}</div>
                  <div className="match-info">
                    <div>
                      <strong>Animal:</strong> {match.animal_name}
                    </div>
                    <div>
                      <strong>Foster:</strong> {match.foster_name}
                    </div>
                  </div>
                  <div>
                    <strong>Reasons:</strong>
                    <ul className="match-reasons">
                      {match.reasons.map((reason, i) => (
                        <li key={i}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                  {(user.role === 'admin' || user.role === 'coordinator') && (
                    <button
                      className="btn btn-success"
                      onClick={() => handleCreatePlacement(match)}
                      style={{marginTop: '1rem'}}
                    >
                      Create Placement
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'profile' && (
        <FosterProfileManager profile={profile} showForm={showProfileForm} onUpdate={loadProfile} />
      )}

      {activeTab === 'placements' && (
        <div className="card">
          <h3>Foster Placements</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Animal ID</th>
                  <th>Foster ID</th>
                  <th>Start Date</th>
                  <th>Status</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {placements.map((placement) => (
                  <tr key={placement.id}>
                    <td>{placement.animal_id}</td>
                    <td>{placement.foster_profile_id}</td>
                    <td>{new Date(placement.start_date).toLocaleDateString()}</td>
                    <td><span className={`badge badge-${placement.outcome}`}>{placement.outcome}</span></td>
                    <td>{placement.placement_notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}

function FosterProfileManager({ profile, showForm, onUpdate }) {
  const [formData, setFormData] = useState({
    experience_level: 'beginner',
    preferred_species: '',
    max_capacity: 1,
    home_type: 'house',
    has_yard: false,
    has_other_pets: false,
    has_children: false,
    can_handle_medical: false,
    can_handle_behavioral: false
  });

  useEffect(() => {
    if (profile) {
      setFormData({
        experience_level: profile.experience_level,
        preferred_species: profile.preferred_species || '',
        max_capacity: profile.max_capacity,
        home_type: profile.home_type || 'house',
        has_yard: profile.has_yard,
        has_other_pets: profile.has_other_pets,
        has_children: profile.has_children,
        can_handle_medical: profile.can_handle_medical,
        can_handle_behavioral: profile.can_handle_behavioral
      });
    }
  }, [profile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (profile) {
        await api.updateMyFosterProfile(formData);
      } else {
        await api.createFosterProfile(formData);
      }
      alert('Profile saved successfully!');
      onUpdate();
    } catch (error) {
      alert('Failed to save profile');
    }
  };

  if (!showForm && profile) {
    return (
      <div className="card">
        <h3>My Foster Profile</h3>
        <div className="grid grid-2">
          <div>
            <p><strong>Experience Level:</strong> {profile.experience_level}</p>
            <p><strong>Preferred Species:</strong> {profile.preferred_species || 'None'}</p>
            <p><strong>Capacity:</strong> {profile.current_capacity} / {profile.max_capacity}</p>
            <p><strong>Home Type:</strong> {profile.home_type}</p>
          </div>
          <div>
            <p><strong>Has Yard:</strong> {profile.has_yard ? 'Yes' : 'No'}</p>
            <p><strong>Has Other Pets:</strong> {profile.has_other_pets ? 'Yes' : 'No'}</p>
            <p><strong>Has Children:</strong> {profile.has_children ? 'Yes' : 'No'}</p>
            <p><strong>Can Handle Medical:</strong> {profile.can_handle_medical ? 'Yes' : 'No'}</p>
            <p><strong>Can Handle Behavioral:</strong> {profile.can_handle_behavioral ? 'Yes' : 'No'}</p>
          </div>
        </div>
        <div style={{marginTop: '1rem'}}>
          <p><strong>Total Fosters:</strong> {profile.total_fosters}</p>
          <p><strong>Successful Adoptions:</strong> {profile.successful_adoptions}</p>
          {profile.rating && <p><strong>Rating:</strong> {profile.rating.toFixed(1)} ⭐</p>}
        </div>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>Edit Profile</button>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>{profile ? 'Edit' : 'Create'} Foster Profile</h3>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-2">
          <div className="form-group">
            <label>Experience Level</label>
            <select
              value={formData.experience_level}
              onChange={(e) => setFormData({...formData, experience_level: e.target.value})}
            >
              <option value="none">None</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div className="form-group">
            <label>Preferred Species (comma-separated)</label>
            <input
              type="text"
              value={formData.preferred_species}
              onChange={(e) => setFormData({...formData, preferred_species: e.target.value})}
              placeholder="Dog, Cat"
            />
          </div>

          <div className="form-group">
            <label>Max Capacity</label>
            <input
              type="number"
              value={formData.max_capacity}
              onChange={(e) => setFormData({...formData, max_capacity: parseInt(e.target.value)})}
              min="1"
              required
            />
          </div>

          <div className="form-group">
            <label>Home Type</label>
            <select
              value={formData.home_type}
              onChange={(e) => setFormData({...formData, home_type: e.target.value})}
            >
              <option value="house">House</option>
              <option value="apartment">Apartment</option>
              <option value="condo">Condo</option>
              <option value="townhouse">Townhouse</option>
            </select>
          </div>
        </div>

        <div className="grid grid-2" style={{marginTop: '1rem'}}>
          <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <input
              type="checkbox"
              checked={formData.has_yard}
              onChange={(e) => setFormData({...formData, has_yard: e.target.checked})}
            />
            Has Yard
          </label>

          <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <input
              type="checkbox"
              checked={formData.has_other_pets}
              onChange={(e) => setFormData({...formData, has_other_pets: e.target.checked})}
            />
            Has Other Pets
          </label>

          <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <input
              type="checkbox"
              checked={formData.has_children}
              onChange={(e) => setFormData({...formData, has_children: e.target.checked})}
            />
            Has Children
          </label>

          <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <input
              type="checkbox"
              checked={formData.can_handle_medical}
              onChange={(e) => setFormData({...formData, can_handle_medical: e.target.checked})}
            />
            Can Handle Medical Needs
          </label>

          <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <input
              type="checkbox"
              checked={formData.can_handle_behavioral}
              onChange={(e) => setFormData({...formData, can_handle_behavioral: e.target.checked})}
            />
            Can Handle Behavioral Issues
          </label>
        </div>

        <button type="submit" className="btn btn-primary" style={{marginTop: '1.5rem'}}>
          {profile ? 'Update' : 'Create'} Profile
        </button>
      </form>
    </div>
  );
}

// OPERATIONS PAGE (Sprint 3)
function OperationsPage() {
  const [activeTab, setActiveTab] = useState('care-updates');
  const [careUpdates, setCareUpdates] = useState([]);
  const [report, setReport] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    if (activeTab === 'care-updates') {
      loadCareUpdates();
    } else if (activeTab === 'reports') {
      loadReport();
    }
  }, [activeTab]);

  const loadCareUpdates = async () => {
    try {
      const response = await api.getCareUpdates();
      setCareUpdates(response.data);
    } catch (error) {
      console.error('Failed to load care updates:', error);
    }
  };

  const loadReport = async () => {
    try {
      const response = await api.getAnimalReport();
      setReport(response.data);
    } catch (error) {
      console.error('Failed to load report:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    const query = e.target.query.value;
    try {
      const response = await api.searchAnimals({ query });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  return (
    <>
      <h2 style={{marginBottom: '1.5rem'}}>Operations</h2>

      <div style={{marginBottom: '1.5rem'}}>
        <button
          className={`btn ${activeTab === 'care-updates' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('care-updates')}
          style={{marginRight: '0.5rem'}}
        >
          Care Updates
        </button>
        <button
          className={`btn ${activeTab === 'search' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('search')}
          style={{marginRight: '0.5rem'}}
        >
          Search & Filter
        </button>
        <button
          className={`btn ${activeTab === 'reports' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('reports')}
        >
          Reports
        </button>
      </div>

      {activeTab === 'care-updates' && (
        <div className="card">
          <h3>Care Updates</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Animal ID</th>
                  <th>Type</th>
                  <th>Update</th>
                  <th>Important</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {careUpdates.map((update) => (
                  <tr key={update.id}>
                    <td>{update.animal_id}</td>
                    <td><span className="badge badge-active">{update.update_type}</span></td>
                    <td>{update.update_text}</td>
                    <td>{update.is_important ? '⭐' : '-'}</td>
                    <td>{new Date(update.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'search' && (
        <div>
          <div className="card">
            <h3>Search Animals</h3>
            <form onSubmit={handleSearch}>
              <div style={{display: 'flex', gap: '0.5rem'}}>
                <input
                  type="text"
                  name="query"
                  placeholder="Search by name, breed, or description..."
                  style={{flex: 1}}
                />
                <button type="submit" className="btn btn-primary">Search</button>
              </div>
            </form>
          </div>

          {searchResults.length > 0 && (
            <div className="grid grid-3">
              {searchResults.map((animal) => (
                <div key={animal.id} className="animal-card">
                  <div className="animal-card-image">
                    {animal.photo_url ? (
                      <img src={animal.photo_url} alt={animal.name} />
                    ) : (
                      <span>No Photo</span>
                    )}
                  </div>
                  <div className="animal-card-content">
                    <h3>{animal.name}</h3>
                    <p><strong>{animal.species}</strong> - {animal.breed || 'Unknown'}</p>
                    <p><span className={`badge badge-${animal.status}`}>{animal.status}</span></p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'reports' && report && (
        <div>
          <div className="card">
            <h3>Animal Statistics Report</h3>
            <p><strong>Total Animals:</strong> {report.total_count}</p>

            <h4 style={{marginTop: '1.5rem'}}>By Status</h4>
            <div className="grid grid-3">
              {Object.entries(report.by_status).map(([status, count]) => (
                <div key={status} className="stat-card">
                  <div className="stat-value">{count}</div>
                  <div className="stat-label">{status}</div>
                </div>
              ))}
            </div>

            <h4 style={{marginTop: '1.5rem'}}>By Species</h4>
            <div className="grid grid-3">
              {Object.entries(report.by_species).map(([species, count]) => (
                <div key={species} className="stat-card">
                  <div className="stat-value">{count}</div>
                  <div className="stat-label">{species}</div>
                </div>
              ))}
            </div>

            {report.average_time_to_foster && (
              <p style={{marginTop: '1.5rem'}}>
                <strong>Avg Time to Foster:</strong> {report.average_time_to_foster.toFixed(1)} days
              </p>
            )}
            {report.average_time_to_adoption && (
              <p>
                <strong>Avg Time to Adoption:</strong> {report.average_time_to_adoption.toFixed(1)} days
              </p>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// ADMIN PAGE (Sprint 4)
function AdminPage() {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [orgInfo, setOrgInfo] = useState(null);

  useEffect(() => {
    if (activeTab === 'users') {
      loadUsers();
    } else if (activeTab === 'config') {
      loadConfig();
    } else if (activeTab === 'organization') {
      loadOrgInfo();
    }
  }, [activeTab]);

  const loadUsers = async () => {
    try {
      const response = await api.getUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const loadConfig = async () => {
    try {
      const response = await api.getSystemConfig();
      setConfigs(response.data);
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadOrgInfo = async () => {
    try {
      const response = await api.getOrganizationInfo();
      setOrgInfo(response.data);
    } catch (error) {
      console.error('Failed to load org info:', error);
    }
  };

  const handleRoleChange = async (userId, role) => {
    try {
      await api.updateUserRole(userId, role);
      alert('Role updated successfully!');
      loadUsers();
    } catch (error) {
      alert('Failed to update role');
    }
  };

  const handleStatusChange = async (userId, isActive) => {
    try {
      await api.updateUserStatus(userId, isActive);
      alert('Status updated successfully!');
      loadUsers();
    } catch (error) {
      alert('Failed to update status');
    }
  };

  return (
    <>
      <h2 style={{marginBottom: '1.5rem'}}>Admin Panel</h2>

      <div style={{marginBottom: '1.5rem'}}>
        <button
          className={`btn ${activeTab === 'users' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('users')}
          style={{marginRight: '0.5rem'}}
        >
          User Management
        </button>
        <button
          className={`btn ${activeTab === 'config' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('config')}
          style={{marginRight: '0.5rem'}}
        >
          System Config
        </button>
        <button
          className={`btn ${activeTab === 'organization' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('organization')}
        >
          Organization
        </button>
      </div>

      {activeTab === 'users' && (
        <div className="card">
          <h3>Users</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.full_name}</td>
                    <td>{user.email}</td>
                    <td>
                      <select
                        value={user.role}
                        onChange={(e) => handleRoleChange(user.id, e.target.value)}
                        className="btn-small"
                      >
                        <option value="admin">Admin</option>
                        <option value="coordinator">Coordinator</option>
                        <option value="foster">Foster</option>
                        <option value="staff">Staff</option>
                      </select>
                    </td>
                    <td>
                      <span className={`badge ${user.is_active ? 'badge-active' : 'badge-returned'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-small btn-secondary"
                        onClick={() => handleStatusChange(user.id, !user.is_active)}
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'config' && (
        <div className="card">
          <h3>System Configuration</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Value</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {configs.map((config) => (
                  <tr key={config.id}>
                    <td><strong>{config.key}</strong></td>
                    <td>{config.value || '-'}</td>
                    <td>{config.description || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'organization' && orgInfo && (
        <div className="card">
          <h3>Organization Information</h3>
          <p><strong>Name:</strong> {orgInfo.name}</p>
          <p><strong>Created:</strong> {new Date(orgInfo.created_at).toLocaleDateString()}</p>

          <h4 style={{marginTop: '1.5rem'}}>Statistics</h4>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{orgInfo.stats.total_users}</div>
              <div className="stat-label">Total Users</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{orgInfo.stats.total_animals}</div>
              <div className="stat-label">Total Animals</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{orgInfo.stats.total_fosters}</div>
              <div className="stat-label">Total Fosters</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
