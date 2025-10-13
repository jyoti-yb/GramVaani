// 🔒 Auth validation helpers

export const validateLogin = (values: { username: string; password: string }) => {
  const errors: Record<string, string> = {};

  if (!values.username.trim()) {
    errors.username = "Username is required.";
  } else if (values.username.length < 3) {
    errors.username = "Username must be at least 3 characters.";
  }

  if (!values.password.trim()) {
    errors.password = "Password is required.";
  } else if (values.password.length < 6) {
    errors.password = "Password must be at least 6 characters.";
  }

  return errors;
};

export const validateSignup = (values: { fullName: string; username: string; email: string; password: string }) => {
  const errors: Record<string, string> = {};

   if (!values.fullName.trim()) {
    errors.fullName = "Full name is required.";
  } else if (values.fullName.length < 2) {
    errors.fullName = "Full name must be at least 2 characters.";
  }

  if (!values.username.trim()) {
    errors.username = "Username is required.";
  } else if (values.username.length < 3) {
    errors.username = "Username must be at least 3 characters.";
  } else if (!/^[a-zA-Z0-9_]+$/.test(values.username)) {
    errors.username = "Username can only contain letters, numbers, and underscores.";
  }

  if (!values.email.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(values.email)) {
    errors.email = "Please enter a valid email address.";
  }

  if (!values.password.trim()) {
    errors.password = "Password is required.";
  } else if (values.password.length < 6) {
    errors.password = "Password must be at least 6 characters.";
  }

  return errors;
};
