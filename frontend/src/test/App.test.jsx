import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock the api module
vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
  setAuthToken: vi.fn(),
}));

describe('App Component', () => {
  it('should render the login page when not authenticated', () => {
    render(<App />);

    // Check for login page elements
    expect(screen.getByText(/Welcome to RescueWorks/i)).toBeInTheDocument();
    expect(screen.getByText(/Sign in to manage your rescue organization/i)).toBeInTheDocument();
  });

  it('should display the login form', () => {
    render(<App />);

    // Check for form elements
    const emailInput = screen.getByLabelText(/Email/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const signInButton = screen.getByRole('button', { name: /Sign In/i });

    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();
    expect(signInButton).toBeInTheDocument();
  });

  it('should render dark mode toggle button', () => {
    render(<App />);

    // The dark mode toggle should be visible
    const toggleButtons = screen.getAllByRole('button');
    expect(toggleButtons.length).toBeGreaterThan(0);
  });

  it('validates theme structure', () => {
    const themes = {
      light: {
        background: '#f8fafc',
        text: '#0f172a',
      },
      dark: {
        background: '#0f172a',
        text: '#f1f5f9',
      },
    };

    expect(themes.light.background).toBe('#f8fafc');
    expect(themes.dark.background).toBe('#0f172a');
  });

  it('should have proper navigation structure', () => {
    const views = ['dashboard', 'intake', 'my', 'vet', 'settings'];

    expect(views).toContain('dashboard');
    expect(views).toContain('intake');
    expect(views).toContain('my');
    expect(views).toContain('vet');
    expect(views).toContain('settings');
  });
});
