import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, 
         GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Your web app's Firebase configuration

const firebaseConfig = {
  apiKey: "AIzaSyAkl8M1qPDIEV4qWHaFJTv926fL6fKgpJE",
  authDomain: "flask-insta.firebaseapp.com",
  projectId: "flask-insta",
  storageBucket: "flask-insta.firebasestorage.app",
  messagingSenderId: "569480683822",
  appId: "1:569480683822:web:34ab3ffbcee2818e8c5abf",
  measurementId: "G-WD1LD32Z9V"
};

  // Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const db = getFirestore(app);

export { auth, provider, db };