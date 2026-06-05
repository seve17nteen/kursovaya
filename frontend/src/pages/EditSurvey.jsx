import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getSurvey, getCategories, updateSurvey } from '../api/surveys';
import './CreateSurvey.css';

export default function EditSurvey() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [isPublished, setIsPublished] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([getSurvey(id), getCategories()])
      .then(([surveyRes, categoriesRes]) => {
        const survey = surveyRes.data;
        const categories = categoriesRes.data.results || categoriesRes.data;
        setCategories(categories);
        setTitle(survey.title || '');
        setDescription(survey.description || '');
        setCategoryId(survey.category?.id || '');
        setIsAnonymous(!!survey.is_anonymous);
        setIsPublished(!!survey.is_published);
      })
      .catch(() => setError('Не удалось загрузить опрос для редактирования'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await updateSurvey(id, {
        title,
        description,
        category: categoryId,
        is_anonymous: isAnonymous,
        is_published: isPublished,
      });
      navigate(`/surveys/${id}`);
    } catch {
      setError('Не удалось сохранить изменения');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="create-survey">
      <h1>Редактирование опроса</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Название опроса *</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Описание</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows="4" />
        </div>
        <div className="form-group">
          <label>Категория *</label>
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} required>
            <option value="">Выберите категорию</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.title}</option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" checked={isAnonymous} onChange={(e) => setIsAnonymous(e.target.checked)} />
              Анонимный опрос
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" checked={isPublished} onChange={(e) => setIsPublished(e.target.checked)} />
              Опубликован
            </label>
          </div>
        </div>
        <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
          {saving ? 'Сохранение...' : 'Сохранить изменения'}
        </button>
      </form>
    </div>
  );
}
