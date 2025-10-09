import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';
import {
  
  Home,
  FolderKanban,
  Users,
  Lightbulb,
  LogOut,
  User,
  LifeBuoy,
  MessageSquare,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Explore' },
    { path: '/projects', icon: FolderKanban, label: 'Projects' },
    { path: '/teams', icon: Users, label: 'Teams' },
    { path: '/ideas', icon: Lightbulb, label: 'Ideas' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
            <div className="w-12 h-12 flex items-center justify-center">
              <img
                src="/logo3.png"
                alt="Campulse"
                className="w-10 h-10 object-contain mix-blend-multiply dark:mix-blend-screen dark:filter dark:brightness-125 transition-all"
              />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Campulse
            </h1>
          </div>

          {/* Nav Items */}
          <div className="hidden md:flex items-center gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Button
                  key={item.path}
                  variant={isActive ? 'default' : 'ghost'}
                  onClick={() => navigate(item.path)}
                  className={
                    isActive
                      ? 'bg-gradient-primary hover:opacity-90'
                      : 'hover:bg-primary/10'
                  }
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </Button>
              );
            })}
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-3">
            <ThemeToggle />
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar>
                    <AvatarFallback className="bg-primary/10 text-primary">
                      <User className="h-5 w-5" />
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-2 py-2">
                  <p className="font-semibold">{user?.fullName || user?.username}</p>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigate('/profile')}>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/support')}>
                  <LifeBuoy className="mr-2 h-4 w-4" />
                  Support
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigate('/feedback')}>
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Feedback
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Mobile Nav */}
        <div className="md:hidden flex items-center gap-2 mt-4 overflow-x-auto pb-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Button
                key={item.path}
                variant={isActive ? 'default' : 'ghost'}
                size="sm"
                onClick={() => navigate(item.path)}
                className={
                  isActive
                    ? 'bg-gradient-primary hover:opacity-90 flex-shrink-0'
                    : 'hover:bg-primary/10 flex-shrink-0'
                }
              >
                <Icon className="w-4 h-4 mr-2" />
                {item.label}
              </Button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
