import { render, screen } from '@testing-library/react';
import App from './App';

test('renders secure access portal', () => {
  render(<App />);
  const headingElement = screen.getByText(/secure access portal/i);
  expect(headingElement).toBeInTheDocument();
});
