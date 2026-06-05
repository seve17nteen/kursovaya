import api from './axios';

// ==================== Auth ====================

export const registerUser = (userData) =>
  api.post('/auth/register/', userData);

export const loginUser = (credentials) =>
  api.post('/auth/login/', credentials);

export const refreshToken = (refresh) =>
  api.post('/auth/token/refresh/', { refresh });

export const getProfile = () =>
  api.get('/auth/profile/');

export const updateProfile = (data) =>
  api.patch('/auth/profile/', data);

// ==================== Surveys ====================

export const getSurveys = (params) =>
  api.get('/surveys/', { params });

export const getSurvey = (id) =>
  api.get(`/surveys/${id}/`);

export const createSurvey = (data) =>
  api.post('/surveys/', data);

export const updateSurvey = (id, data) =>
  api.patch(`/surveys/${id}/`, data);

export const deleteSurvey = (id) =>
  api.delete(`/surveys/${id}/`);

export const getMySurveys = (params) =>
  api.get('/surveys/my/', { params });

export const getSurveyStats = (id) =>
  api.get(`/surveys/${id}/stats/`);

export const incrementViews = (id) =>
  api.post(`/surveys/${id}/increment_views/`);

export const submitResponse = (id, answers) =>
  api.post(`/surveys/${id}/submit_response/`, { answers });

// ==================== Categories ====================

export const getCategories = () =>
  api.get('/categories/');

// ==================== Questions ====================

export const getQuestions = (surveyId) =>
  api.get(`/questions/?survey=${surveyId}`);

export const createQuestion = (data) =>
  api.post('/questions/', data);

export const updateQuestion = (id, data) =>
  api.patch(`/questions/${id}/`, data);

export const deleteQuestion = (id) =>
  api.delete(`/questions/${id}/`);

// ==================== Comments ====================

export const getComments = (surveyId) =>
  api.get(`/comments/?survey=${surveyId}`);

export const createComment = (data) =>
  api.post('/comments/', data);

export const deleteComment = (id) =>
  api.delete(`/comments/${id}/`);

// ==================== Responses ====================

export const getMyResponses = (params) =>
  api.get('/responses/', { params });
