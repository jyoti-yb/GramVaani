import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Mail, Instagram, ExternalLink } from 'lucide-react';

const Support = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-hero bg-clip-text text-transparent">
            We're Here to Help
          </h1>
          <p className="text-xl text-muted-foreground">
            Get in touch with the Campulse team
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="border-border/50 shadow-lg hover:shadow-xl transition-shadow animate-fade-in">
            <CardHeader>
              <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center mb-4">
                <Mail className="w-6 h-6 text-white" />
              </div>
              <CardTitle>Email Support</CardTitle>
              <CardDescription>Send us an email and we'll get back to you</CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                className="w-full justify-between group hover:border-primary/50"
                onClick={() => window.open('mailto:infocampulse2025@gmail.com')}
              >
                infocampulse2025@gmail.com
                <ExternalLink className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>

          <Card className="border-border/50 shadow-lg hover:shadow-xl transition-shadow animate-fade-in" style={{ animationDelay: '100ms' }}>
            <CardHeader>
              <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center mb-4">
                <Instagram className="w-6 h-6 text-white" />
              </div>
              <CardTitle>Follow Us</CardTitle>
              <CardDescription>Stay updated with our latest news</CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                className="w-full justify-between group hover:border-primary/50"
                onClick={() => window.open('https://www.instagram.com/campulse2025/', '_blank')}
              >
                @campulse2025
                <ExternalLink className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-8 border-border/50 shadow-lg animate-fade-in" style={{ animationDelay: '200ms' }}>
          <CardHeader>
            <CardTitle>About Campulse</CardTitle>
            <CardDescription>Empowering student collaboration</CardDescription>
          </CardHeader>
          <CardContent className="prose dark:prose-invert max-w-none">
            <p className="text-muted-foreground">
              Campulse is a dedicated platform designed to help students connect, collaborate, and bring their innovative project ideas to life. Whether you're looking for team members, seeking feedback on your ideas, or wanting to showcase your work, Campulse provides the tools and community to make it happen.
            </p>
            <p className="text-muted-foreground mt-4">
              Our mission is to foster a vibrant ecosystem of student innovation where creativity meets collaboration, and ideas transform into reality.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Support;
