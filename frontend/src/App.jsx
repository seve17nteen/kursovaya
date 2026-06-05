import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import SurveyDetail from './pages/SurveyDetail';
import CreateSurvey from './pages/CreateSurvey';
import MySurveys from './pages/MySurveys';
import Profile from './pages/Profile';
import EditSurvey from './pages/EditSurvey';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/surveys/:id" element={<SurveyDetail />} />
            <Route
              path="/surveys/create"
              element={
                <ProtectedRoute>
                  <CreateSurvey />
                </ProtectedRoute>
              }
            />
            <Route
              path="/surveys/my"
              element={
                <ProtectedRoute>
                  <MySurveys />
                </ProtectedRoute>
              }
            />
            <Route
              path="/surveys/:id/edit"
              element={
                <ProtectedRoute>
                  <EditSurvey />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
