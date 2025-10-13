import { useEffect, useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ideasAPI, profileAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Plus, Loader2, Trash2, MessageSquare, Send, Eye, ExternalLink, Github, Linkedin, Phone } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';

interface Idea {
  id: number;
  title: string;
  teamLead: string;
  description: string;
  fullName: string;
  date: string;
}

interface Comment {
  id: number;
  title: string;
  comment: string;
  username: string;
}

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

const Ideas = () => {
  const { user } = useAuth();
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showCommentsDialog, setShowCommentsDialog] = useState(false);
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [newIdea, setNewIdea] = useState({
    title: '',
    description: '',
  });

  useEffect(() => {
    loadIdeas();
  }, []);

  const loadIdeas = async () => {
    try {
      const response = await ideasAPI.getAll();
      // Ensure all ideas have required fields with defaults
      const ideasWithDefaults = (response.data || []).map((idea: any) => ({
        ...idea,
        teamLead: idea.teamLead || 'Unknown',
        fullName: idea.fullName || 'Unknown User',
        description: idea.description || '',
        title: idea.title || 'Untitled',
        date: idea.date || new Date().toISOString().split('T')[0],
      }));
      // Sort ideas by date (newest first)
      const sortedIdeas = ideasWithDefaults.sort((a: Idea, b: Idea) => 
        new Date(b.date).getTime() - new Date(a.date).getTime()
      );
      setIdeas(sortedIdeas);
    } catch (error) {
      toast.error('Failed to load ideas');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateIdea = async () => {
    if (!newIdea.title || !newIdea.description) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      await ideasAPI.add({
        ...newIdea,
        teamLead: user?.username,
        fullName: user?.fullName || user?.username,
        date: new Date().toISOString().split('T')[0],
      });
      toast.success('Idea posted successfully!');
      setShowCreateDialog(false);
      setNewIdea({ title: '', description: '' });
      loadIdeas();
    } catch (error) {
      toast.error('Failed to post idea');
    }
  };

  const handleDeleteIdea = async (title: string) => {
    if (!confirm('Are you sure you want to delete this idea?')) return;

    try {
      await ideasAPI.delete(title);
      toast.success('Idea deleted successfully');
      loadIdeas();
    } catch (error) {
      toast.error('Failed to delete idea');
    }
  };

  const loadComments = async (title: string) => {
    try {
      const response = await ideasAPI.getComments(title);
      // Ensure all comments have username field
      const commentsWithDefaults = (response.data || []).map((comment: any) => ({
        ...comment,
        username: comment.username || 'Anonymous',
        comment: comment.comment || '',
      }));
      setComments(commentsWithDefaults);
    } catch (error) {
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedIdea) return;

    try {
      await ideasAPI.addComment({
        title: selectedIdea.title,
        comment: newComment,
        username: user?.username,
      });
      setNewComment('');
      loadComments(selectedIdea.title);
      toast.success('Comment added!');
    } catch (error) {
      toast.error('Failed to add comment');
    }
  };

  const handleDeleteComment = async (id: number) => {
    if (!confirm('Delete this comment?')) return;

    try {
      await ideasAPI.deleteComment(id);
      if (selectedIdea) {
        loadComments(selectedIdea.title);
      }
      toast.success('Comment deleted');
    } catch (error) {
      toast.error('Failed to delete comment');
    }
  };

  const loadProfile = async (username: string) => {
    try {
      const response = await profileAPI.get(username);
      const profileData = response.data;
      
      const profileWithDefaults = {
        ...profileData,
        username: profileData.username || username,
        fullName: profileData.fullName || 'Unknown User',
        branch: profileData.branch || 'Not specified',
        college: profileData.college || 'Not specified',
        year: profileData.year || 0,
        projects: profileData.projects || [],
        skills: profileData.skills || [],
        interests: profileData.interests || [],
        achievements: profileData.achievements || [],
        bio: profileData.bio || '',
        phone: profileData.phone || '',
        githubLink: profileData.githubLink || '',
        linkedinLink: profileData.linkedinLink || '',
      };
      
      setSelectedProfile(profileWithDefaults);
      setShowProfileDialog(true);
    } catch (error) {
      toast.error('Failed to load profile');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-hero bg-clip-text text-transparent mb-2">
              Project Ideas
            </h1>
            <p className="text-muted-foreground">
              Share your ideas and get validation from the community
            </p>
          </div>
          <Button onClick={() => setShowCreateDialog(true)} className="bg-gradient-primary hover:opacity-90">
            <Plus className="mr-2 h-4 w-4" />
            Share Idea
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          </div>
        ) : ideas.length === 0 ? (
          <Card className="p-12 text-center">
            <p className="text-muted-foreground">No ideas yet. Be the first to share!</p>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ideas.map((idea) => (
              <Card key={idea.id} className="border-border/50 shadow-lg hover:shadow-xl transition-all animate-fade-in">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{idea.title}</CardTitle>
                      <div className="flex items-center gap-2">
                        <Avatar className="h-6 w-6">
                          <AvatarFallback className="bg-gradient-primary text-white text-xs">
                            {(idea.teamLead || 'U').charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <Button
                          variant="link"
                          className="p-0 h-auto text-sm text-muted-foreground hover:text-primary"
                          onClick={() => loadProfile(idea.teamLead)}
                        >
                          {idea.fullName || 'Unknown'}
                        </Button>
                      </div>
                    </div>
                    {idea.teamLead === user?.username && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteIdea(idea.title)}
                        className="text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground line-clamp-4">{idea.description}</p>
                  <p className="text-xs text-muted-foreground mt-4">
                    Posted on {new Date(idea.date).toLocaleDateString()}
                  </p>
                </CardContent>
                <CardFooter>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full gap-2"
                    onClick={() => {
                      setSelectedIdea(idea);
                      loadComments(idea.title);
                      setShowCommentsDialog(true);
                    }}
                  >
                    <MessageSquare className="h-4 w-4" />
                    Validate & Comment
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create Idea Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Share Your Idea</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Idea Title *</Label>
              <Input
                id="title"
                placeholder="e.g., AI-Powered Study Planner"
                value={newIdea.title}
                onChange={(e) => setNewIdea({ ...newIdea, title: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                rows={6}
                placeholder="Describe your idea in detail. What problem does it solve? Who is it for?"
                value={newIdea.description}
                onChange={(e) => setNewIdea({ ...newIdea, description: e.target.value })}
              />
            </div>
            <Button onClick={handleCreateIdea} className="w-full bg-gradient-primary hover:opacity-90">
              Share Idea
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Comments Dialog */}
      <Dialog open={showCommentsDialog} onOpenChange={setShowCommentsDialog}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedIdea?.title}</DialogTitle>
          </DialogHeader>
          
          {selectedIdea && (
            <div className="space-y-6">
              {/* Idea Details */}
              <div className="p-4 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-2 mb-3">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-gradient-primary text-white">
                      {(selectedIdea.teamLead || 'U').charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <Button
                      variant="link"
                      className="p-0 h-auto font-semibold text-sm hover:text-primary"
                      onClick={() => loadProfile(selectedIdea.teamLead)}
                    >
                      {selectedIdea.fullName || 'Unknown'}
                    </Button>
                    <p className="text-xs text-muted-foreground">
                      {new Date(selectedIdea.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <p className="text-sm whitespace-pre-wrap">{selectedIdea.description}</p>
              </div>

              {/* Add Comment */}
              <div className="space-y-2">
                <Label>Add Your Validation & Feedback</Label>
                <div className="flex gap-2">
                  <Textarea
                    placeholder="Share your thoughts, suggestions, or validation..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleAddComment())}
                    rows={3}
                    className="flex-1"
                  />
                  <Button onClick={handleAddComment} size="icon" className="bg-gradient-primary h-auto">
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Comments List */}
              <div className="space-y-3">
                <h3 className="font-semibold">Community Feedback</h3>
                {comments.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8 text-sm">
                    No feedback yet. Be the first to validate this idea!
                  </p>
                ) : (
                  comments.map((comment) => (
                    <div
                      key={comment.id}
                      className="p-4 rounded-lg bg-secondary/30 border border-border/50"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <Avatar className="h-6 w-6">
                            <AvatarFallback className="bg-primary/20 text-primary text-xs">
                              {(comment.username || 'A').charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <Button
                            variant="link"
                            className="p-0 h-auto font-semibold text-sm hover:text-primary"
                            onClick={() => loadProfile(comment.username)}
                          >
                            {comment.username || 'Anonymous'}
                          </Button>
                        </div>
                        {comment.username === user?.username && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteComment(comment.id)}
                            className="text-destructive hover:bg-destructive/10 h-8 w-8"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                      <p className="text-sm whitespace-pre-wrap">{comment.comment}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Profile Dialog */}
      <Dialog open={showProfileDialog} onOpenChange={setShowProfileDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Profile Details</DialogTitle>
          </DialogHeader>
          {selectedProfile && (
            <div className="space-y-6">
              <div className="text-center">
                <Avatar className="w-24 h-24 mx-auto mb-4">
                  <AvatarFallback className="bg-gradient-primary text-white text-3xl">
                    {(selectedProfile.fullName || 'U').charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <h2 className="text-2xl font-bold">{selectedProfile.fullName || 'Unknown User'}</h2>
                <p className="text-muted-foreground">@{selectedProfile.username || 'unknown'}</p>
              </div>

              {selectedProfile.bio && (
                <div>
                  <h3 className="font-semibold mb-2">Bio</h3>
                  <p className="text-sm text-muted-foreground">{selectedProfile.bio}</p>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">Education</h3>
                  <p className="text-sm">{selectedProfile.college || 'Not specified'}</p>
                  <p className="text-sm text-muted-foreground">{selectedProfile.branch || 'Not specified'}</p>
                  <p className="text-sm text-muted-foreground">Year {selectedProfile.year || 'N/A'}</p>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold mb-2">Contact</h3>
                  {selectedProfile.phone && (
                    <Button variant="outline" size="sm" className="w-full justify-start gap-2">
                      <Phone className="h-4 w-4" />
                      {selectedProfile.phone}
                    </Button>
                  )}
                  {selectedProfile.githubLink && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start gap-2"
                      onClick={() => window.open(selectedProfile.githubLink, '_blank')}
                    >
                      <Github className="h-4 w-4" />
                      GitHub
                      <ExternalLink className="h-3 w-3 ml-auto" />
                    </Button>
                  )}
                  {selectedProfile.linkedinLink && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full justify-start gap-2"
                      onClick={() => window.open(selectedProfile.linkedinLink, '_blank')}
                    >
                      <Linkedin className="h-4 w-4" />
                      LinkedIn
                      <ExternalLink className="h-3 w-3 ml-auto" />
                    </Button>
                  )}
                </div>
              </div>

              {(selectedProfile.skills || []).length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedProfile.skills || []).map((skill, i) => (
                      <Badge key={i} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {(selectedProfile.projects || []).length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Projects</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {(selectedProfile.projects || []).map((project, i) => (
                      <li key={i} className="text-sm text-muted-foreground">{project}</li>
                    ))}
                  </ul>
                </div>
              )}

              {(selectedProfile.interests || []).length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Interests</h3>
                  <div className="flex flex-wrap gap-2">
                    {(selectedProfile.interests || []).map((interest, i) => (
                      <Badge key={i} variant="outline">{interest}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {(selectedProfile.achievements || []).length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Achievements</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {(selectedProfile.achievements || []).map((achievement, i) => (
                      <li key={i} className="text-sm text-muted-foreground">{achievement}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Ideas;
