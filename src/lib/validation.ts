// 🔒 Auth validation helpers

export const validateLogin = (values: { username: string; password: string }) => {
  const errors: Record<string, string> = {};

  if (!values.username.trim()) {
    errors.username = "Username is required.";
  } else if (!/^(23000)\d{5}$/.test(values.username)) {
    errors.username = "Username must start with 23000 and be exactly 10 digits.";
  }

  if (!values.password.trim()) {
    errors.password = "Password is required.";
  } else if (values.password.length < 5) {
    errors.password = "Password must be at least 5 characters.";
  }

  return errors;
};

export const validateSignup = (values: { fullName: string; username: string; email: string; password: string }) => {
  const errors: Record<string, string> = {};

  if (!values.fullName.trim()) {
    errors.fullName = "Full name is required.";
  }

  if (!values.username.trim()) {
    errors.username = "Username is required.";
  } else if (!/^(23000)\d{5}$/.test(values.username)) {
    errors.username = "Username must start with 23000 and be exactly 10 digits.";
  }

  if (!values.email.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[A-Za-z0-9._%+-]+@kluniversity\.in$/.test(values.email)) {
    errors.email = "Email must end with @kluniversity.in.";
  }

  if (!values.password.trim()) {
    errors.password = "Password is required.";
  } else if (values.password.length < 5) {
    errors.password = "Password must be at least 5 characters.";
  }

  return errors;
};
