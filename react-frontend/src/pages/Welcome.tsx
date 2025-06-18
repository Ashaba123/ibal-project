import { Link } from 'react-router-dom';
import './Welcome.css';

const Welcome = () => {
  return (
    <div className="welcome-container">
      <div className="welcome-content">
        <h1>Welcome to IBAL Chat</h1>
        <p>Your intelligent conversation partner</p>
        <div className="welcome-buttons">
          <Link to="/login" className="btn btn-primary">
            Login
          </Link>
          <Link to="/register" className="btn btn-secondary">
            Register
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Welcome; 