import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ThemeToggle } from '@/components/ThemeToggle';
import { profileAPI } from '@/lib/api';
import { toast } from 'sonner';
import { Loader2, Plus, X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const CompleteProfile = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const username = localStorage.getItem('signup_username') || '';
  
  const [formData, setFormData] = useState({
    username,
    fullName: '',
    branch: '',
    college: '',
    year: 1,
    bio: '',
    phone: '',
    githubLink: '',
    linkedinLink: '',
  });

  const [projects, setProjects] = useState<string[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [interests, setInterests] = useState<string[]>([]);
  const [achievements, setAchievements] = useState<string[]>([]);

  const [currentInput, setCurrentInput] = useState({
    project: '',
    skill: '',
    interest: '',
    achievement: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const addItem = (type: 'project' | 'skill' | 'interest' | 'achievement') => {
    const value = currentInput[type].trim();
    if (!value) return;

    switch (type) {
      case 'project':
        setProjects([...projects, value]);
        break;
      case 'skill':
        setSkills([...skills, value]);
        break;
      case 'interest':
        setInterests([...interests, value]);
        break;
      case 'achievement':
        setAchievements([...achievements, value]);
        break;
    }
    setCurrentInput({ ...currentInput, [type]: '' });
  };

  const removeItem = (type: 'project' | 'skill' | 'interest' | 'achievement', index: number) => {
    switch (type) {
      case 'project':
        setProjects(projects.filter((_, i) => i !== index));
        break;
      case 'skill':
        setSkills(skills.filter((_, i) => i !== index));
        break;
      case 'interest':
        setInterests(interests.filter((_, i) => i !== index));
        break;
      case 'achievement':
        setAchievements(achievements.filter((_, i) => i !== index));
        break;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await profileAPI.create({
        ...formData,
        year: parseInt(formData.year.toString()),
        projects,
        skills,
        interests,
        achievements,
      });
      toast.success('Profile completed successfully!');
      localStorage.removeItem('signup_username');
      navigate('/login');
    } catch (error: any) {
      toast.error(error.response?.data || 'Failed to create profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/20 to-background p-6">
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="container mx-auto max-w-3xl py-12">
        <Card className="border-border/50 shadow-2xl animate-scale-in">
          <CardHeader className="text-center space-y-4">
            <div className="mx-auto w-24 h-24 flex items-center justify-center">
              <img
                src="/logo3.png"
                alt="Campulse"
                className="w-20 h-20 object-contain mix-blend-multiply dark:mix-blend-screen dark:filter dark:brightness-125 transition-all"
              />
            </div>
            <CardTitle className="text-3xl font-bold">Complete Your Profile</CardTitle>
            <CardDescription>Tell us more about yourself to get started</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="fullName">Full Name *</Label>
                  <Input
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="college">College *</Label>
                  <Input
                    id="college"
                    name="college"
                    value={formData.college}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="branch">Branch/Major *</Label>
                  <Input
                    id="branch"
                    name="branch"
                    value={formData.branch}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="year">Year of Study *</Label>
                <Input
                  id="year"
                  name="year"
                  type="number"
                  min="1"
                  max="5"
                  value={formData.year}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  name="bio"
                  placeholder="Tell us about yourself..."
                  value={formData.bio}
                  onChange={handleChange}
                  rows={3}
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="githubLink">GitHub Profile</Label>
                  <Input
                    id="githubLink"
                    name="githubLink"
                    placeholder="https://github.com/username"
                    value={formData.githubLink}
                    onChange={handleChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="linkedinLink">LinkedIn Profile</Label>
                  <Input
                    id="linkedinLink"
                    name="linkedinLink"
                    placeholder="https://linkedin.com/in/username"
                    value={formData.linkedinLink}
                    onChange={handleChange}
                  />
                </div>
              </div>

              {/* Skills */}
              <div className="space-y-2">
                <Label>Skills</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add a skill..."
                    value={currentInput.skill}
                    onChange={(e) => setCurrentInput({ ...currentInput, skill: e.target.value })}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('skill'))}
                  />
                  <Button type="button" onClick={() => addItem('skill')} size="icon" variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {skills.map((skill, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {skill}
                      <X
                        className="h-3 w-3 cursor-pointer hover:text-destructive"
                        onClick={() => removeItem('skill', index)}
                      />
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Projects */}
              <div className="space-y-2">
                <Label>Projects</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add a project..."
                    value={currentInput.project}
                    onChange={(e) => setCurrentInput({ ...currentInput, project: e.target.value })}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('project'))}
                  />
                  <Button type="button" onClick={() => addItem('project')} size="icon" variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {projects.map((project, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {project}
                      <X
                        className="h-3 w-3 cursor-pointer hover:text-destructive"
                        onClick={() => removeItem('project', index)}
                      />
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Interests */}
              <div className="space-y-2">
                <Label>Interests</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add an interest..."
                    value={currentInput.interest}
                    onChange={(e) => setCurrentInput({ ...currentInput, interest: e.target.value })}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('interest'))}
                  />
                  <Button type="button" onClick={() => addItem('interest')} size="icon" variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {interests.map((interest, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {interest}
                      <X
                        className="h-3 w-3 cursor-pointer hover:text-destructive"
                        onClick={() => removeItem('interest', index)}
                      />
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Achievements */}
              <div className="space-y-2">
                <Label>Achievements</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add an achievement..."
                    value={currentInput.achievement}
                    onChange={(e) => setCurrentInput({ ...currentInput, achievement: e.target.value })}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('achievement'))}
                  />
                  <Button type="button" onClick={() => addItem('achievement')} size="icon" variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {achievements.map((achievement, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {achievement}
                      <X
                        className="h-3 w-3 cursor-pointer hover:text-destructive"
                        onClick={() => removeItem('achievement', index)}
                      />
                    </Badge>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-gradient-primary hover:opacity-90 transition-opacity"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Profile...
                  </>
                ) : (
                  'Complete Profile'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CompleteProfile;
