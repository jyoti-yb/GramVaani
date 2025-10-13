import { useEffect, useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { profileAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Loader2, Edit2, Save, X, Plus, ExternalLink, Github, Linkedin, Phone, Mail } from 'lucide-react';

interface Profile {
  username: string;
  fullName: string;
  branch: string;
  college: string;
  year: number;
  projects: string[];
  skills: string[];
  interests: string[];
  achievements: string[];
  bio: string;
  phone: string;
  githubLink: string;
  linkedinLink: string;
}

const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [creating, setCreating] = useState(false);
  const [editedProfile, setEditedProfile] = useState<Profile | null>(null);
  const [currentInput, setCurrentInput] = useState({
    project: '',
    skill: '',
    interest: '',
    achievement: '',
  });

  useEffect(() => {
    loadProfile();
  }, [user]);

  const loadProfile = async () => {
    if (!user) return;
    try {
      const response = await profileAPI.get(user.username);
      setProfile(response.data);
      setEditedProfile(response.data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!editedProfile) return;
    setSaving(true);

    try {
      await profileAPI.update(editedProfile);
      setProfile(editedProfile);
      setEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCreate = async () => {
    if (!user) return;
    setCreating(true);
    const newProfile: Profile = {
      username: user.username,
      fullName: user.fullName || '',
      branch: '',
      college: '',
      year: 1,
      projects: [],
      skills: [],
      interests: [],
      achievements: [],
      bio: '',
      phone: '',
      githubLink: '',
      linkedinLink: '',
    };

    try {
      const response = await profileAPI.create(newProfile);
      const created = response.data;
      setProfile(created);
      setEditedProfile(created);
      setEditing(true);
      toast.success('Profile created! You can now edit your details.');
    } catch (error) {
      toast.error('Failed to create profile');
    } finally {
      setCreating(false);
    }
  };

  const handleCancel = () => {
    setEditedProfile(profile);
    setEditing(false);
  };

  const addItem = (type: 'project' | 'skill' | 'interest' | 'achievement') => {
    if (!editedProfile || !currentInput[type].trim()) return;

    const newProfile = { ...editedProfile };
    switch (type) {
      case 'project':
        newProfile.projects = [...newProfile.projects, currentInput[type]];
        break;
      case 'skill':
        newProfile.skills = [...newProfile.skills, currentInput[type]];
        break;
      case 'interest':
        newProfile.interests = [...newProfile.interests, currentInput[type]];
        break;
      case 'achievement':
        newProfile.achievements = [...newProfile.achievements, currentInput[type]];
        break;
    }
    setEditedProfile(newProfile);
    setCurrentInput({ ...currentInput, [type]: '' });
  };

  const removeItem = (type: 'project' | 'skill' | 'interest' | 'achievement', index: number) => {
    if (!editedProfile) return;

    const newProfile = { ...editedProfile };
    switch (type) {
      case 'project':
        newProfile.projects = newProfile.projects.filter((_, i) => i !== index);
        break;
      case 'skill':
        newProfile.skills = newProfile.skills.filter((_, i) => i !== index);
        break;
      case 'interest':
        newProfile.interests = newProfile.interests.filter((_, i) => i !== index);
        break;
      case 'achievement':
        newProfile.achievements = newProfile.achievements.filter((_, i) => i !== index);
        break;
    }
    setEditedProfile(newProfile);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-6 py-12 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
        </div>
      </div>
    );
  }

  if (!profile || !editedProfile) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container mx-auto px-6 py-12">
          <Card className="p-12 text-center">
            <p className="text-muted-foreground mb-6">Profile not found. Create your profile to get started.</p>
            <Button onClick={handleCreate} disabled={creating} className="bg-gradient-primary hover:opacity-90">
              {creating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Profile
                </>
              )}
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold bg-gradient-hero bg-clip-text text-transparent">
            My Profile
          </h1>
          {!editing ? (
            <Button onClick={() => setEditing(true)} className="bg-gradient-primary hover:opacity-90">
              <Edit2 className="mr-2 h-4 w-4" />
              Edit Profile
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleCancel}>
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving} className="bg-gradient-primary hover:opacity-90">
                {saving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Profile Header */}
        <Card className="mb-6 border-border/50 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <Avatar className="w-24 h-24">
                <AvatarFallback className="bg-gradient-primary text-white text-4xl">
                  {profile.fullName.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 text-center md:text-left">
                {editing ? (
                  <div className="space-y-3">
                    <Input
                      value={editedProfile.fullName}
                      onChange={(e) => setEditedProfile({ ...editedProfile, fullName: e.target.value })}
                      className="text-2xl font-bold"
                    />
                    <Input
                      value={editedProfile.bio}
                      onChange={(e) => setEditedProfile({ ...editedProfile, bio: e.target.value })}
                      placeholder="Bio"
                    />
                  </div>
                ) : (
                  <>
                    <h2 className="text-3xl font-bold">{profile.fullName}</h2>
                    <p className="text-muted-foreground mt-1">@{profile.username}</p>
                    {profile.bio && <p className="text-sm mt-2">{profile.bio}</p>}
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Education */}
        <Card className="mb-6 border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Education</CardTitle>
          </CardHeader>
          <CardContent>
            {editing ? (
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>College</Label>
                  <Input
                    value={editedProfile.college}
                    onChange={(e) => setEditedProfile({ ...editedProfile, college: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Branch/Major</Label>
                  <Input
                    value={editedProfile.branch}
                    onChange={(e) => setEditedProfile({ ...editedProfile, branch: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Year of Study</Label>
                  <Input
                    type="number"
                    min="1"
                    max="5"
                    value={editedProfile.year}
                    onChange={(e) => setEditedProfile({ ...editedProfile, year: parseInt(e.target.value) })}
                  />
                </div>
              </div>
            ) : (
              <div>
                <p className="font-semibold">{profile.college}</p>
                <p className="text-muted-foreground">{profile.branch}</p>
                <p className="text-sm text-muted-foreground">Year {profile.year}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Contact */}
        <Card className="mb-6 border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {editing ? (
              <>
                <div className="space-y-2">
                  <Label>Phone</Label>
                  <Input
                    value={editedProfile.phone}
                    onChange={(e) => setEditedProfile({ ...editedProfile, phone: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>GitHub</Label>
                  <Input
                    value={editedProfile.githubLink}
                    onChange={(e) => setEditedProfile({ ...editedProfile, githubLink: e.target.value })}
                    placeholder="https://github.com/username"
                  />
                </div>
                <div className="space-y-2">
                  <Label>LinkedIn</Label>
                  <Input
                    value={editedProfile.linkedinLink}
                    onChange={(e) => setEditedProfile({ ...editedProfile, linkedinLink: e.target.value })}
                    placeholder="https://linkedin.com/in/username"
                  />
                </div>
              </>
            ) : (
              <>
                {profile.phone && (
                  <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                    <Phone className="h-4 w-4" />
                    {profile.phone}
                  </Button>
                )}
                {profile.githubLink && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start gap-2"
                    onClick={() => window.open(profile.githubLink, '_blank')}
                  >
                    <Github className="h-4 w-4" />
                    GitHub
                    <ExternalLink className="h-3 w-3 ml-auto" />
                  </Button>
                )}
                {profile.linkedinLink && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start gap-2"
                    onClick={() => window.open(profile.linkedinLink, '_blank')}
                  >
                    <Linkedin className="h-4 w-4" />
                    LinkedIn
                    <ExternalLink className="h-3 w-3 ml-auto" />
                  </Button>
                )}
              </>
            )}
          </CardContent>
        </Card>

        {/* Skills */}
        <Card className="mb-6 border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Skills</CardTitle>
          </CardHeader>
          <CardContent>
            {editing && (
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Add skill..."
                  value={currentInput.skill}
                  onChange={(e) => setCurrentInput({ ...currentInput, skill: e.target.value })}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('skill'))}
                />
                <Button onClick={() => addItem('skill')} size="icon" variant="secondary">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              {editedProfile.skills.map((skill, i) => (
                <Badge key={i} variant="secondary" className={editing ? 'gap-1' : ''}>
                  {skill}
                  {editing && (
                    <X className="h-3 w-3 cursor-pointer" onClick={() => removeItem('skill', i)} />
                  )}
                </Badge>
              ))}
              {editedProfile.skills.length === 0 && (
                <p className="text-sm text-muted-foreground">No skills added yet</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Projects */}
        <Card className="mb-6 border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent>
            {editing && (
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Add project..."
                  value={currentInput.project}
                  onChange={(e) => setCurrentInput({ ...currentInput, project: e.target.value })}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('project'))}
                />
                <Button onClick={() => addItem('project')} size="icon" variant="secondary">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
            {editedProfile.projects.length === 0 ? (
              <p className="text-sm text-muted-foreground">No projects added yet</p>
            ) : (
              <ul className="space-y-2">
                {editedProfile.projects.map((project, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span className="flex-1">{project}</span>
                    {editing && (
                      <X
                        className="h-4 w-4 cursor-pointer text-destructive hover:text-destructive/80"
                        onClick={() => removeItem('project', i)}
                      />
                    )}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Interests */}
        <Card className="mb-6 border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Interests</CardTitle>
          </CardHeader>
          <CardContent>
            {editing && (
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Add interest..."
                  value={currentInput.interest}
                  onChange={(e) => setCurrentInput({ ...currentInput, interest: e.target.value })}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('interest'))}
                />
                <Button onClick={() => addItem('interest')} size="icon" variant="secondary">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
            <div className="flex flex-wrap gap-2">
              {editedProfile.interests.map((interest, i) => (
                <Badge key={i} variant="outline" className={editing ? 'gap-1' : ''}>
                  {interest}
                  {editing && (
                    <X className="h-3 w-3 cursor-pointer" onClick={() => removeItem('interest', i)} />
                  )}
                </Badge>
              ))}
              {editedProfile.interests.length === 0 && (
                <p className="text-sm text-muted-foreground">No interests added yet</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Achievements */}
        <Card className="border-border/50 shadow-lg">
          <CardHeader>
            <CardTitle>Achievements</CardTitle>
          </CardHeader>
          <CardContent>
            {editing && (
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Add achievement..."
                  value={currentInput.achievement}
                  onChange={(e) => setCurrentInput({ ...currentInput, achievement: e.target.value })}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addItem('achievement'))}
                />
                <Button onClick={() => addItem('achievement')} size="icon" variant="secondary">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
            {editedProfile.achievements.length === 0 ? (
              <p className="text-sm text-muted-foreground">No achievements added yet</p>
            ) : (
              <ul className="space-y-2">
                {editedProfile.achievements.map((achievement, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span className="flex-1">{achievement}</span>
                    {editing && (
                      <X
                        className="h-4 w-4 cursor-pointer text-destructive hover:text-destructive/80"
                        onClick={() => removeItem('achievement', i)}
                      />
                    )}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
