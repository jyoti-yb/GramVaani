import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ThemeToggle } from '@/components/ThemeToggle';
import { userAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { validateLogin } from '@/lib/validation';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const validationErrors = validateLogin(formData);
    setErrors(validationErrors);
    
    if (Object.keys(validationErrors).length > 0) {
      toast.error('Please fix the validation errors');
      return;
    }
    
    setLoading(true);

    console.log('🔐 Attempting login for username:', formData.username);

    try {
      const response = await userAPI.login(formData);
      console.log('📥 Login response:', response);
      console.log('📥 Response data:', response.data);
      console.log('📥 Response status:', response.status);

      // Check if login was successful - backend returns specific success message
      if (response.status === 200 && typeof response.data === 'string' && response.data.includes('Login successful')) {
        console.log('✅ Login successful!');
        
        // Fetch user details and store in context
        login({
          username: formData.username,
          email: '', // Will be updated from profile
          fullName: '', // Will be updated from profile
        });
        
        toast.success('Welcome back!');
        console.log('🚀 Navigating to dashboard...');
        navigate('/dashboard');
      } else {
        console.log('❌ Unexpected response:', response.data);
        toast.error('Invalid username or password');
      }
    } catch (error: any) {
      console.error('❌ Login error:', error);
      console.error('Error response:', error.response);
      console.error('Error message:', error.message);
      
      // Backend returns error for wrong credentials
      if (error.response?.status === 400 || error.response?.status === 401) {
        toast.error('Invalid username or password');
      } else {
        const errorMessage = error.response?.data || error.message || 'Login failed. Please check your credentials.';
        toast.error(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-secondary/20 to-background p-6">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <Card className="w-full max-w-md border-border/50 shadow-2xl animate-scale-in">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-24 h-24 flex items-center justify-center">
            <img
              src="/logo3.png"
              alt="Campulse"
              className="w-20 h-20 object-contain mix-blend-multiply dark:mix-blend-screen dark:filter dark:brightness-125 transition-all"
            />
          </div>
          <CardTitle className="text-3xl font-bold">Welcome Back</CardTitle>
          <CardDescription>Sign in to continue to Campulse</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                name="username"
                placeholder="2300012345"
                value={formData.username}
                onChange={handleChange}
                required
              />
              {errors.username && (
                <p className="text-sm text-destructive">{errors.username}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password}</p>
              )}
            </div>
            <Button
              type="submit"
              className="w-full bg-gradient-primary hover:opacity-90 transition-opacity"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
          <div className="mt-6 text-center space-y-3">
            <Button
              variant="link"
              className="text-primary hover:text-primary/80"
              onClick={() => {
                const username = prompt('Enter your username:');
                if (username) {
                  userAPI.forgotPassword(username)
                    .then(() => toast.success('Password sent to your email'))
                    .catch(() => toast.error('User not found'));
                }
              }}
            >
              Forgot password?
            </Button>
            <div className="text-sm">
              <span className="text-muted-foreground">Don't have an account? </span>
              <Button
                variant="link"
                className="p-0 text-primary hover:text-primary/80"
                onClick={() => navigate('/signup')}
              >
                Sign up
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
