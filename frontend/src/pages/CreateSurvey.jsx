import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createSurvey, getCategories, createQuestion, getSurvey } from '../api/surveys';
import './CreateSurvey.css';

export default function CreateSurvey() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCategories()
      .then(({ data }) => setCategories(data.results || data))
      .catch(() => {});
  }, []);

  const addQuestion = () => {
    setQuestions([...questions, {
      key: Date.now(),
      text: '',
      question_type: 'radio',
      required: true,
      choices: [{ key: Date.now() + 1, text: '' }, { key: Date.now() + 2, text: '' }],
    }]);
  };

  const removeQuestion = (key) => {
    setQuestions(questions.filter((q) => q.key !== key));
  };

  const updateQuestion = (key, field, value) => {
    setQuestions(questions.map((q) =>
      q.key === key ? { ...q, [field]: value } : q
    ));
  };

  const addChoice = (qKey) => {
    setQuestions(questions.map((q) =>
      q.key === qKey
        ? { ...q, choices: [...q.choices, { key: Date.now(), text: '' }] }
        : q
    ));
  };

  const removeChoice = (qKey, cKey) => {
    setQuestions(questions.map((q) =>
      q.key === qKey
        ? { ...q, choices: q.choices.filter((c) => c.key !== cKey) }
        : q
    ));
  };

  const updateChoice = (qKey, cKey, text) => {
    setQuestions(questions.map((q) =>
      q.key === qKey
        ? {
            ...q,
            choices: q.choices.map((c) =>
              c.key === cKey ? { ...c, text } : c
            ),
          }
        : q
    ));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!categoryId) {
      setError('Выберите категорию');
      return;
    }

    if (questions.length === 0) {
      setError('Добавьте хотя бы один вопрос');
      return;
    }

    setLoading(true);
    try {
      // Создаём опрос
      const { data: survey } = await createSurvey({
        title,
        description,
        category: categoryId,
        is_published: true,
        is_anonymous: isAnonymous,
      });

      // Создаём вопросы
      for (const q of questions) {
        const questionData = {
          survey: survey.id,
          text: q.text,
          question_type: q.question_type,
          required: q.required,
          order: questions.indexOf(q),
        };

        if (q.question_type !== 'text') {
          questionData.choices = q.choices
            .filter((c) => c.text.trim())
            .map((c, i) => ({ text: c.text, order: i }));
        }

        await createQuestion(questionData);
      }

      navigate(`/surveys/${survey.id}`);
    } catch (err) {
      setError('Ошибка при создании опроса');
      setLoading(false);
    }
  };

  return (
    <div className="create-survey">
      <h1>Создание опроса</h1>
      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Название опроса *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Введите название"
          />
        </div>

        <div className="form-group">
          <label>Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="4"
            placeholder="Опишите цель опроса"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Категория *</label>
            <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} required>
              <option value="">Выберите категорию</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.title}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>&nbsp;</label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
              />
              Анонимный опрос
            </label>
          </div>
        </div>

        <div className="questions-section">
          <h3>Вопросы</h3>

          {questions.map((q, idx) => (
            <div key={q.key} className="question-editor">
              <div className="question-header">
                <span>Вопрос {idx + 1}</span>
                <button type="button" onClick={() => removeQuestion(q.key)}
                  className="btn btn-sm btn-danger-text">
                  Удалить
                </button>
              </div>

              <div className="form-group">
                <input
                  type="text"
                  value={q.text}
                  onChange={(e) => updateQuestion(q.key, 'text', e.target.value)}
                  placeholder="Текст вопроса"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <select
                    value={q.question_type}
                    onChange={(e) => updateQuestion(q.key, 'question_type', e.target.value)}
                  >
                    <option value="radio">Один вариант</option>
                    <option value="checkbox">Несколько вариантов</option>
                    <option value="text">Текстовый ответ</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={q.required}
                      onChange={(e) => updateQuestion(q.key, 'required', e.target.checked)}
                    />
                    Обязательный
                  </label>
                </div>
              </div>

              {q.question_type !== 'text' && (
                <div className="choices-editor">
                  {q.choices.map((c, cIdx) => (
                    <div key={c.key} className="choice-row">
                      <span className="choice-number">{cIdx + 1}.</span>
                      <input
                        type="text"
                        value={c.text}
                        onChange={(e) => updateChoice(q.key, c.key, e.target.value)}
                        placeholder={`Вариант ${cIdx + 1}`}
                        required={cIdx < 2}
                      />
                      {q.choices.length > 2 && (
                        <button type="button"
                          onClick={() => removeChoice(q.key, c.key)}
                          className="btn btn-sm btn-danger-text">
                          &times;
                        </button>
                      )}
                    </div>
                  ))}
                  <button type="button" onClick={() => addChoice(q.key)}
                    className="btn btn-sm btn-outline">
                    + Добавить вариант
                  </button>
                </div>
              )}
            </div>
          ))}

          <button type="button" onClick={addQuestion}
            className="btn btn-outline btn-block">
            + Добавить вопрос
          </button>
        </div>

        <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
          {loading ? 'Создание...' : 'Создать опрос'}
        </button>
      </form>
    </div>
  );
}
