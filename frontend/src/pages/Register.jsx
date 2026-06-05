import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: '', email: '', password: '', password2: '',
    first_name: '', last_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.password2) {
      setError('Пароли не совпадают');
      return;
    }

    setLoading(true);
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      const data = err.response?.data;
      if (data) {
        const messages = Object.values(data).flat().join('; ');
        setError(messages);
      } else {
        setError('Ошибка регистрации');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Регистрация</h2>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Имя</label>
              <input name="first_name" value={form.first_name}
                onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Фамилия</label>
              <input name="last_name" value={form.last_name}
                onChange={handleChange} />
            </div>
          </div>
          <div className="form-group">
            <label>Имя пользователя *</label>
            <input name="username" value={form.username}
              onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input type="email" name="email" value={form.email}
              onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Пароль *</label>
            <input type="password" name="password"
              value={form.password} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Подтверждение пароля *</label>
            <input type="password" name="password2"
              value={form.password2} onChange={handleChange} required />
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="auth-link">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  );
}
