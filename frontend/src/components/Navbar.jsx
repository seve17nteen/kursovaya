import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { isAuthenticated, isAdmin, user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          Опросник
        </Link>
        <div className="navbar-links">
          <Link to="/" className="nav-link">Главная</Link>
          {isAuthenticated && (
            <>
              <Link to="/surveys/create" className="nav-link">Создать опрос</Link>
              <Link to="/surveys/my" className="nav-link">Мои опросы</Link>
            </>
          )}
        </div>
        <div className="navbar-auth">
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="nav-link">
                {user?.username}
                {isAdmin && <span className="admin-badge">Админ</span>}
              </Link>
              <button onClick={logout} className="btn btn-sm btn-outline">
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-sm btn-outline">Войти</Link>
              <Link to="/register" className="btn btn-sm btn-primary">Регистрация</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
