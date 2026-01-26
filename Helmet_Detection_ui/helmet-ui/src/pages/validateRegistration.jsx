export const validateForm = (formData) => {
  const errors = {};

  // Aadhar Validation
  if (!formData.aadhar_no.trim()) {
    errors.aadhar_no = "Aadhar number is required";
  } else if (!/^\d{12}$/.test(formData.aadhar_no)) {
    errors.aadhar_no = "Aadhar number must be a 12-digit number";
  }

  // Full Name Validation
  if (!formData.full_name.trim()) {
    errors.full_name = "Full name is required";
  } else if (!/^[A-Za-z ]{3,}$/.test(formData.full_name)) {
    errors.full_name = "Name should contain only letters and be at least 3 characters";
  }

  // Date of Birth Validation
 if (!formData.dob.trim()) {
  errors.dob = "Date of birth is required";
} else {
  const dob = new Date(formData.dob);
  const today = new Date();

  if (dob >= today) {
    errors.dob = "Date of birth must be in the past";
  } else {
    // Calculate age
    const age = today.getFullYear() - dob.getFullYear();
    const monthDiff = today.getMonth() - dob.getMonth();
    const dayDiff = today.getDate() - dob.getDate();

    // Adjust if birthday hasn't occurred yet this year
    const adjustedAge =
      monthDiff > 0 || (monthDiff === 0 && dayDiff >= 0) ? age : age - 1;

    if (adjustedAge < 18) {
      errors.dob = "You must be at least 18 years old";
    }
  }
}


  // Email Validation
  if (!formData.email.trim()) {
    errors.email = "Email is required";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = "Enter a valid email address";
  }

  // Phone Number Validation
  if (!formData.phone.trim()) {
    errors.phone = "Phone number is required";
  } else if (!/^[6-9]\d{9}$/.test(formData.phone)) {
    errors.phone = "Phone number must be a 10-digit number starting with 6–9";
  }
  return errors;
};
