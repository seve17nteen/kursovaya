import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Profile() {
  const { user, updateUserProfile, logout } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    bio: user?.bio || '',
    phone: user?.phone || '',
  });
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      await updateUserProfile(form);
      setSuccess('Профиль обновлён');
    } catch (err) {
      setError('Ошибка при обновлении');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Профиль</h2>
        {success && <div className="alert alert-success">{success}</div>}
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Имя</label>
              <input name="first_name" value={form.first_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Фамилия</label>
              <input name="last_name" value={form.last_name} onChange={handleChange} />
            </div>
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" value={form.email} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Телефон</label>
            <input name="phone" value={form.phone} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>О себе</label>
            <textarea name="bio" value={form.bio} onChange={handleChange} rows="3" />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </form>
        <div className="profile-info">
          <p>Имя пользователя: <strong>{user?.username}</strong></p>
        </div>
        <button onClick={logout} className="btn btn-danger-text btn-block" style={{ marginTop: 16 }}>
          Выйти из аккаунта
        </button>
      </div>
    </div>
  );
}
