import React, { useState } from 'react';

interface PasswordInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  minLength?: number;
  id?: string;
  name?: string;
  className?: string;
}

const PasswordInput: React.FC<PasswordInputProps> = ({
  value,
  onChange,
  placeholder = "Enter your password",
  required = false,
  disabled = false,
  minLength,
  id = "password",
  name = "password",
  className = ""
}) => {
  const [showPassword, setShowPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="password-input-container">
      <input
        type={showPassword ? "text" : "password"}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        placeholder={placeholder}
        minLength={minLength}
        className={className}
      />
      <button
        type="button"
        className="password-toggle"
        onClick={togglePasswordVisibility}
        tabIndex={-1}
      >
        {showPassword ? "Hide" : "Show"}
      </button>
    </div>
  );
};

export default PasswordInput; 