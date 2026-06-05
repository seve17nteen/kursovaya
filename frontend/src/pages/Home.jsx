import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getSurveys, getCategories } from '../api/surveys';
import './Home.css';

export default function Home() {
  const [surveys, setSurveys] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    getCategories()
      .then(({ data }) => setCategories(data.results || data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = { page };
    if (search) params.search = search;
    if (selectedCategory) params.category = selectedCategory;

    getSurveys(params)
      .then(({ data }) => {
        setSurveys(data.results || data);
        setTotalPages(Math.ceil((data.count || 0) / 10) || 1);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [search, selectedCategory, page]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
  };

  return (
    <div className="home">
      <div className="home-header">
        <h1>Опросы и анкеты</h1>
        <p>Создавайте опросы, проходите анкеты, анализируйте результаты</p>
      </div>

      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Поиск опросов..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select
          value={selectedCategory}
          onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
        >
          <option value="">Все категории</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>{cat.title}</option>
          ))}
        </select>
        <button type="submit" className="btn btn-primary">Найти</button>
      </form>

      {loading ? (
        <div className="loading">Загрузка опросов...</div>
      ) : surveys.length === 0 ? (
        <div className="empty">
          <p>Опросы не найдены</p>
        </div>
      ) : (
        <>
          <div className="survey-grid">
            {surveys.map((survey) => (
              <div key={survey.id} className="survey-card">
                <div className="card-category">{survey.category_title}</div>
                <h3 className="card-title">
                  <Link to={`/surveys/${survey.id}`}>{survey.title}</Link>
                </h3>
                <p className="card-description">
                  {survey.description?.slice(0, 150)}
                  {survey.description?.length > 150 ? '...' : ''}
                </p>
                <div className="card-meta">
                  <span>{survey.questions_count} вопр.</span>
                  <span>{survey.responses_count} отв.</span>
                  <span>{survey.views} просм.</span>
                </div>
                <div className="card-footer">
                  <span className="card-author">{survey.author_name}</span>
                  <span className="card-date">
                    {new Date(survey.created_at).toLocaleDateString('ru-RU')}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="btn btn-outline"
            >
              Назад
            </button>
            <span>Стр. {page} из {totalPages}</span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="btn btn-outline"
            >
              Вперёд
            </button>
          </div>
        </>
      )}
    </div>
  );
}
