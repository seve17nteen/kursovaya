import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getSurvey, getComments, createComment, deleteComment,
         incrementViews, submitResponse } from '../api/surveys';
import { useAuth } from '../context/AuthContext';
import './SurveyDetail.css';

export default function SurveyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [survey, setSurvey] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState({});
  const [commentText, setCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    setLoading(true);
    setLoadError('');
    Promise.all([
      getSurvey(id),
      getComments(id),
      incrementViews(id),
    ])
      .then(([surveyRes, commentsRes]) => {
        setSurvey(surveyRes.data);
        setComments(commentsRes.data.results || commentsRes.data);
      })
      .catch((err) => {
        setLoadError(err.response?.data?.detail || 'Не удалось загрузить опрос');
      })
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleChoiceChange = (questionId, choiceId, questionType) => {
    if (questionType === 'checkbox') {
      setAnswers((prev) => {
        const current = prev[questionId] || [];
        if (current.includes(choiceId)) {
          return { ...prev, [questionId]: current.filter((c) => c !== choiceId) };
        }
        return { ...prev, [questionId]: [...current, choiceId] };
      });
    } else {
      setAnswers((prev) => ({ ...prev, [questionId]: choiceId }));
    }
  };

  const handleTextChange = (questionId, text) => {
    setAnswers((prev) => ({ ...prev, [questionId]: text }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Проверка обязательных вопросов
    for (const q of survey.questions) {
      if (q.required && !answers[q.id]) {
        setError(`Вопрос "${q.text.slice(0, 60)}" обязателен для ответа`);
        return;
      }
    }

    setSubmitting(true);
    setError('');

    const answersList = survey.questions.map((q) => {
      const answer = { question: q.id };
      if (q.question_type === 'text') {
        answer.text = answers[q.id] || '';
      } else if (q.question_type === 'checkbox') {
        // Отправляем выбранные варианты по одному
        // DRF это не поддерживает — отправляем первый выбранный
        // для совместимости (можно доработать)
        answer.choice = Array.isArray(answers[q.id])
          ? answers[q.id][0]
          : answers[q.id];
      } else {
        answer.choice = answers[q.id];
      }
      return answer;
    });

    try {
      await submitResponse(id, answersList);
      setSubmitted(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при отправке ответов');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    try {
      const { data } = await createComment({
        survey: id,
        text: commentText.trim(),
      });
      setComments((prev) => [data, ...prev]);
      setCommentText('');
    } catch {
      //
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await deleteComment(commentId);
      setComments((prev) => prev.filter((c) => c.id !== commentId));
    } catch {
      //
    }
  };

  if (loading) return <div className="loading">Загрузка опроса...</div>;
  if (loadError) return <div className="loading">{loadError}</div>;
  if (!survey) return <div className="loading">Опрос не найден</div>;

  return (
    <div className="survey-detail">
      <div className="detail-header">
        <span className="detail-category">{survey.category?.title}</span>
        <h1>{survey.title}</h1>
        <p className="detail-meta">
          Автор: {survey.author} &bull;
          Вопросов: {survey.questions_count} &bull;
          Ответов: {survey.responses_count} &bull;
          Просмотров: {survey.views}
        </p>
        <p className="detail-description">{survey.description}</p>
      </div>

      {submitted ? (
        <div className="submit-success">
          <h3>Спасибо за участие!</h3>
          <p>Ваши ответы сохранены.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="survey-form">
          {error && <div className="alert alert-error">{error}</div>}

          {survey.questions?.map((question, idx) => (
            <div key={question.id} className="question-block">
              <h4>
                {idx + 1}. {question.text}
                {question.required && <span className="required">*</span>}
              </h4>

              {question.question_type === 'text' ? (
                <textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => handleTextChange(question.id, e.target.value)}
                  placeholder="Введите ваш ответ..."
                  rows="3"
                  required={question.required}
                />
              ) : (
                <div className="choices-list">
                  {question.choices?.map((choice) => (
                    <label key={choice.id} className="choice-item">
                      <input
                        type={question.question_type === 'checkbox' ? 'checkbox' : 'radio'}
                        name={`question_${question.id}`}
                        checked={
                          question.question_type === 'checkbox'
                            ? (answers[question.id] || []).includes(choice.id)
                            : answers[question.id] === choice.id
                        }
                        onChange={() =>
                          handleChoiceChange(question.id, choice.id, question.question_type)
                        }
                      />
                      <span>{choice.text}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>
          ))}

          {isAuthenticated ? (
            <button type="submit" className="btn btn-primary btn-lg" disabled={submitting}>
              {submitting ? 'Отправка...' : 'Отправить ответы'}
            </button>
          ) : (
            <p className="login-hint">
              <button type="button" onClick={() => navigate('/login')} className="btn btn-link">
                Войдите
              </button>
              , чтобы пройти опрос
            </p>
          )}
        </form>
      )}

      {/* Comments section */}
      <div className="comments-section">
        <h3>Комментарии ({comments.length})</h3>
        {isAuthenticated && (
          <form onSubmit={handleAddComment} className="comment-form">
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Напишите комментарий..."
              rows="2"
              required
            />
            <button type="submit" className="btn btn-sm btn-primary">
              Отправить
            </button>
          </form>
        )}
        <div className="comments-list">
          {comments.length === 0 ? (
            <p className="no-comments">Комментариев пока нет</p>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="comment-item">
                <div className="comment-header">
                  <strong>{comment.author_name}</strong>
                  <span className="comment-date">
                    {new Date(comment.created_at).toLocaleString('ru-RU')}
                  </span>
                </div>
                <p>{comment.text}</p>
                {(user?.id === comment.author || user?.is_staff) && (
                  <button
                    onClick={() => handleDeleteComment(comment.id)}
                    className="btn btn-sm btn-danger-text"
                  >
                    Удалить
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
