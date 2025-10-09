import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Users, Lightbulb, MessageSquare, ArrowRight } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Users,
      title: 'Find Your Team',
      description: 'Connect with talented individuals who share your passion for innovation',
    },
    {
      icon: Lightbulb,
      title: 'Share Ideas',
      description: 'Validate your project concepts with the community and get valuable feedback',
    },
    {
      icon: MessageSquare,
      title: 'Real-time Chat',
      description: 'Collaborate seamlessly with your team through integrated group messaging',
    },
    {
      // use a small image component for the logo instead of the Sparkles icon
      // let the caller pass sizing via className so it matches other icons
      icon: (props: any) => (
        <img src="/logo3.png" alt="Campulse" className={props?.className ?? ''} />
      ),
      title: 'Showcase Projects',
      description: 'Display your work and discover amazing projects from fellow students',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/20 to-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
            <div className="w-12 h-12 rounded-full flex items-center justify-center">
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
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Button
              variant="ghost"
              onClick={() => navigate('/login')}
              className="hidden sm:flex"
            >
              Login
            </Button>
            <Button
              onClick={() => navigate('/signup')}
              className="bg-gradient-primary hover:opacity-90 transition-opacity"
            >
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center animate-fade-in">
            <h2 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-hero bg-clip-text text-transparent leading-tight">
              Connect. Collaborate. Create
            </h2>
            <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
              Join the ultimate platform for students to collaborate, innovate, and bring their project ideas to life together.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                onClick={() => navigate('/signup')}
                className="bg-gradient-primary hover:opacity-90 transition-all text-lg px-8 py-6 group"
              >
                Start Collaborating
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate('/login')}
                className="border-2 border-primary text-lg px-8 py-6 hover:bg-primary/10"
              >
                Sign In
              </Button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-24">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="w-14 h-14 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  {/* feature.icon might be a component or an inline img component */}
                  <feature.icon className="w-9 h-9 object-contain mix-blend-multiply dark:mix-blend-screen dark:filter dark:brightness-125 transition-all" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto max-w-4xl text-center">
          <h3 className="text-4xl font-bold mb-6">Ready to Build Something Amazing?</h3>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of students already collaborating on Campulse
          </p>
          <Button
            size="lg"
            onClick={() => navigate('/signup')}
            className="bg-gradient-primary hover:opacity-90 transition-all text-lg px-10 py-6"
          >
            Join Campulse Now
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 px-6">
        <div className="container mx-auto text-center text-muted-foreground">
          <p>&copy; 2025 Campulse. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
