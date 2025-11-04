
    // <script>
    //     document.addEventListener('DOMContentLoaded', function () {
    //         const signInToggle = document.getElementById('signInToggle');
    //         const signUpToggle = document.getElementById('signUpToggle');
    //         const signInBox = document.getElementById('signInBox');
    //         const signUpBox = document.getElementById('SignUp-box');
    //         const signupForm = document.getElementById('signupForm'); // ✅ Added
    //         const signinForm = document.getElementById('signinForm'); // ✅ Added

    //         // Initial state
    //         signUpBox.style.display = 'block';
    //         signInBox.style.display = 'none';

    //         // Toggle to Sign In
    //         if (signInToggle) {
    //             signInToggle.addEventListener('click', function (e) {
    //                 e.preventDefault();
    //                 signUpBox.style.display = 'none';
    //                 signInBox.style.display = 'block';
    //                 signInBox.classList.add('show');
    //             });
    //         }

    //         // Toggle to Sign Up
    //         if (signUpToggle) {
    //             signUpToggle.addEventListener('click', function (e) {
    //                 e.preventDefault();
    //                 signInBox.classList.remove('show');
    //                 setTimeout(() => {
    //                     signInBox.style.display = 'none';
    //                     signUpBox.style.display = 'block';
    //                 }, 300);
    //             });
    //         }

    //         // ✅ Handle signup form submission
    //         signupForm.addEventListener('submit', async function (e) {
    //             e.preventDefault(); // stop normal form behavior

    //             const formData = new FormData(signupForm);
    //             const submitButton = signupForm.querySelector('button[type="submit"]');
                
    //             // Disable button during submission
    //             submitButton.disabled = true;
    //             submitButton.textContent = "Creating Account...";

    //             try {
    //                 // change the URL below to match your FastAPI backend
    //                 const response = await fetch("http://127.0.0.1:8000/signup", {
    //                     method: "POST",
    //                     body: formData,
    //                     headers: {
    //                         'Accept': 'application/json',
    //                     }
    //                 });

    //                 const data = await response.json();

    //                 if (response.ok) {
    //                     alert("✅ Sign-up successful! User ID: " + data.user_id);
    //                     signupForm.reset();
    //                     // Optionally switch to sign-in form
    //                     signInBox.style.display = 'block';
    //                     signUpBox.style.display = 'none';
    //                 } else {
    //                     alert("❌ Error: " + (data.detail || "Something went wrong."));
    //                 }
    //             } catch (error) {
    //                 alert("⚠️ Unable to connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000");
    //                 console.error("Connection error:", error);
    //             } finally {
    //                 // Re-enable button
    //                 submitButton.disabled = false;
    //                 submitButton.textContent = "Get Started";
    //             }
    //         });

    //         // ✅ Handle signin form submission
    //         signinForm.addEventListener('submit', async function (e) {
    //             e.preventDefault(); // stop normal form behavior

    //             const formData = new FormData(signinForm);
    //             const submitButton = signinForm.querySelector('button[type="submit"]');
                
    //             // Disable button during submission
    //             submitButton.disabled = true;
    //             submitButton.textContent = "Signing In...";

    //             try {
    //                 const response = await fetch("http://127.0.0.1:8000/signin", {
    //                     method: "POST",
    //                     body: formData,
    //                     headers: {
    //                         'Accept': 'application/json',
    //                     }
    //                 });

    //                 const data = await response.json();

    //                 if (response.ok) {
    //                     alert("✅ Sign-in successful! Welcome back!");
    //                     signinForm.reset();
    //                     // Here you could redirect to a dashboard or main app
    //                     // window.location.href = '/dashboard';
    //                 } else {
    //                     alert("❌ Error: " + (data.detail || "Invalid credentials."));
    //                 }
    //             } catch (error) {
    //                 alert("⚠️ Unable to connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000");
    //                 console.error("Connection error:", error);
    //             } finally {
    //                 // Re-enable button
    //                 submitButton.disabled = false;
    //                 submitButton.textContent = "Sign In";
    //             }
    //         });
    //     });
    // </script>