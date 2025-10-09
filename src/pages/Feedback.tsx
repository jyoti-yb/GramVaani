import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageSquare, ExternalLink } from 'lucide-react';

const Feedback = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-hero bg-clip-text text-transparent">
            Share Your Feedback
          </h1>
          <p className="text-xl text-muted-foreground">
            Help us improve Campulse with your valuable input
          </p>
        </div>

        <Card className="border-border/50 shadow-lg animate-fade-in">
          <CardHeader className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-primary flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl">We Value Your Opinion</CardTitle>
            <CardDescription className="text-base">
              Your feedback helps us create a better experience for all Campulse users
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="p-6 rounded-lg bg-gradient-card border border-border/50">
              <h3 className="font-semibold text-lg mb-2">What We'd Love to Know:</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>How has Campulse helped you in your projects?</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>What features would you like to see added?</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Any suggestions for improving the platform?</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>Your overall experience using Campulse</span>
                </li>
              </ul>
            </div>

            <div className="text-center">
              <Button
                size="lg"
                className="bg-gradient-primary hover:opacity-90 transition-all group"
                onClick={() => window.open('https://forms.gle/Bp25yGX4v3BD3UKKA', '_blank')}
              >
                Open Feedback Form
                <ExternalLink className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Button>
              <p className="text-sm text-muted-foreground mt-4">
                Takes less than 2 minutes to complete
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-8 text-center text-muted-foreground">
          <p>Thank you for being a part of the Campulse community! 💜</p>
        </div>
      </div>
    </div>
  );
};

export default Feedback;
