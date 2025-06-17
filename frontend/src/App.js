import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Generate from './pages/Generate';
import Status from './pages/Status';
import TestPages from './pages/TestPages';
import Documentation from './pages/Documentation';
import About from './pages/About';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Header />
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/generate" element={<Generate />} />
            <Route path="/status/:workflowId" element={<Status />} />
            <Route path="/documentation/:workflowId" element={<Documentation />} />
            <Route path="/test" element={<TestPages />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        
        <Footer />
        
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              className: 'toast-success',
            },
            error: {
              className: 'toast-error',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App; 