import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';


const Dashboard = ({ accessToken }) => {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [selectedNoteId, setSelectedNoteId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotes();
  }, []); // Fetch notes on component mount

  const fetchNotes = async () => {
    try {
      const response = await fetch('http://localhost:8000/notes/', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch notes');
      }
      const data = await response.json();
      setNotes(data);
    } catch (error) {
      console.error('Fetch notes error:', error);
      // Handle error
    }
  };

  const handleCreateNote = async () => {
    try {
      const response = await fetch('http://localhost:8000/notes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ user_id: '', title, description }),
      });
      if (!response.ok) {
        throw new Error('Failed to create note');
      }
      const data = await response.json();
      setNotes([...notes, data]);
      setTitle('');
      setDescription('');
    } catch (error) {
      console.error('Create note error:', error);
      // Handle error
    }
  };

  const handleUpdateNote = async (id, updatedNote) => {
    updatedNote.user_id = ''
    console.log(updatedNote)
    try {
      const response = await fetch(`http://localhost:8000/notes/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(updatedNote),
      });
      if (!response.ok) {
        throw new Error('Failed to update note');
      }
      const updatedNotes = notes.map(note =>
        note.id === id ? { ...note, ...updatedNote } : note
      );
      setNotes(updatedNotes);
      setEditMode(false);
      setTitle('');
      setDescription('');
      setSelectedNoteId(null);
    } catch (error) {
      console.error('Update note error:', error);
      // Handle error
    }
  };

  const handleDeleteNote = async (id) => {
    try {
      const response = await fetch(`http://localhost:8000/notes/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to delete note');
      }
      const filteredNotes = notes.filter(note => note.id !== id);
      setNotes(filteredNotes);
    } catch (error) {
      console.error('Delete note error:', error);
      // Handle error
    }
  };

  const startEditNote = (note) => {
    setSelectedNoteId(note.id);
    setTitle(note.title);
    setDescription(note.description);
    setEditMode(true);
  };

  const cancelEdit = () => {
    setEditMode(false);
    setTitle('');
    setDescription('');
    setSelectedNoteId(null);
  };

  const handleSubmit = () => {
    if (editMode) {
      handleUpdateNote(selectedNoteId, { title, description });
    } else {
      handleCreateNote();
    }
  };

  const handleLogout = () => {
    // Perform any logout logic here (e.g., clearing tokens, etc.)
    Cookies.remove('access_token');
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      <button className="btn btn-danger" onClick={handleLogout}>
        Logout
      </button>
      <div>
        <h3>Your Notes:</h3>
        <div className="notes-list">
          {notes.map((note) => (
            <div key={note.id} className="note-item">
              <strong>{note.title}</strong>
              <p>{note.description}</p>
              <div>
                <button className="btn btn-info" onClick={() => startEditNote(note)}>Update</button>
                <button className="btn btn-danger" onClick={() => handleDeleteNote(note.id)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="create-note-form">
        <h3>{editMode ? 'Edit Note' : 'Create New Note'}:</h3>
        <div className="form-group">
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="form-control"
            required
          />
        </div>
        <div className="form-group">
          <label>Description:</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="form-control"
            rows="3"
            required
          ></textarea>
        </div>
        <button className="btn btn-success" onClick={handleSubmit}>
          {editMode ? 'Update Note' : 'Create Note'}
        </button>
        {editMode && (
          <button className="btn btn-secondary" onClick={cancelEdit}>
            Cancel
          </button>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
