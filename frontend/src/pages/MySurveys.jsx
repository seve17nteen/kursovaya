import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getMySurveys, getSurveyStats, deleteSurvey } from '../api/surveys';
import './MySurveys.css';

export default function MySurveys() {
  const navigate = useNavigate();
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statsMap, setStatsMap] = useState({});

  useEffect(() => {
    getMySurveys()
      .then(({ data }) => {
        setSurveys(data.results || data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить опрос?')) return;
    try {
      await deleteSurvey(id);
      setSurveys((prev) => prev.filter((s) => s.id !== id));
    } catch {
      //
    }
  };

  const toggleStats = async (id) => {
    if (statsMap[id]) {
      setStatsMap((prev) => { const copy = { ...prev }; delete copy[id]; return copy; });
      return;
    }
    try {
      const { data } = await getSurveyStats(id);
      setStatsMap((prev) => ({ ...prev, [id]: data }));
    } catch {
      //
    }
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div className="my-surveys">
      <div className="my-header">
        <h1>Мои опросы</h1>
        <Link to="/surveys/create" className="btn btn-primary">Создать опрос</Link>
      </div>

      {surveys.length === 0 ? (
        <div className="empty">
          <p>У вас пока нет опросов</p>
          <Link to="/surveys/create" className="btn btn-primary">Создать первый</Link>
        </div>
      ) : (
        <div className="survey-list">
          {surveys.map((survey) => (
            <div key={survey.id} className="my-survey-item">
              <div className="my-survey-info">
                <Link to={`/surveys/${survey.id}`} className="my-survey-title">
                  {survey.title}
                </Link>
                <div className="my-survey-meta">
                  <span>{survey.questions_count} вопр.</span>
                  <span>{survey.responses_count} отв.</span>
                  <span>{new Date(survey.created_at).toLocaleDateString('ru-RU')}</span>
                  {!survey.is_published && <span className="draft-badge">Черновик</span>}
                </div>
              </div>
              <div className="my-survey-actions">
                <button onClick={() => toggleStats(survey.id)}
                  className="btn btn-sm btn-outline">
                  Статистика
                </button>
                <button onClick={() => navigate(`/surveys/${survey.id}/edit`)}
                  className="btn btn-sm btn-outline">
                  Ред.
                </button>
                <button onClick={() => handleDelete(survey.id)}
                  className="btn btn-sm btn-danger-text">
                  Удалить
                </button>
              </div>

              {statsMap[survey.id] && (
                <div className="stats-panel">
                  <h4>Статистика ({statsMap[survey.id].total_responses} ответов)</h4>
                  {statsMap[survey.id].questions_stats.map((q) => (
                    <div key={q.question_id} className="stats-question">
                      <p className="stats-q-text">{q.question_text}</p>
                      {q.choices ? (
                        <div className="stats-bars">
                          {q.choices.map((c) => (
                            <div key={c.choice_id} className="stats-bar-row">
                              <span className="stats-bar-label">{c.choice_text}</span>
                              <div className="stats-bar-track">
                                <div
                                  className="stats-bar-fill"
                                  style={{ width: `${c.percentage}%` }}
                                />
                              </div>
                              <span className="stats-bar-value">{c.percentage}% ({c.count})</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="stats-text-count">
                          Текстовых ответов: {q.text_count}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
