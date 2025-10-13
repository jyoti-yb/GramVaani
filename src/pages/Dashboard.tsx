import { useEffect, useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Textarea } from '@/components/ui/textarea';
import { feedAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { MessageCircle, Trash2, Send, Loader2, Eye, ExternalLink, Github, Linkedin, Phone, Plus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { profileAPI } from '@/lib/api';

interface Feed {
  id: number;
  title: string;
  description: string;
  username: string;
  department: string;
}

interface Comment {
  num: number;
  feedId: number;
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

const Dashboard = () => {
  const { user } = useAuth();
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [postLoading, setPostLoading] = useState(false);
  const [newPost, setNewPost] = useState({ title: '', description: '' });
  const [selectedFeed, setSelectedFeed] = useState<Feed | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [showNewPostDialog, setShowNewPostDialog] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);

  useEffect(() => {
    loadFeeds();
  }, []);

  const loadFeeds = async () => {
    try {
      const response = await feedAPI.getAll();
      // Sort feeds by id (newer posts have higher ids)
      const sortedFeeds = (response.data || []).sort((a: Feed, b: Feed) => b.id - a.id);
      setFeeds(sortedFeeds);
    } catch (error) {
      toast.error('Error load feeds');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async () => {
    if (!newPost.title || !newPost.description) {
      toast.error('Please fill in all fields');
      return;
    }

    setPostLoading(true);
    try {
      await feedAPI.upload({
        ...newPost,
        username: user?.username,
        department: '',
      });
      toast.success('Post created successfully!');
      setNewPost({ title: '', description: '' });
      setShowNewPostDialog(false);
      loadFeeds();
    } catch (error: any) {
      toast.error('Failed to create post');
    } finally {
      setPostLoading(false);
    }
  };

  const handleDeletePost = async (id: number) => {
    if (!confirm('Are you sure you want to delete this post?')) return;

    try {
      await feedAPI.delete(id);
      toast.success('Post deleted successfully');
      loadFeeds();
    } catch (error) {
      toast.error('Failed to delete post');
    }
  };

  const loadComments = async (feedId: number) => {
    try {
      const response = await feedAPI.getComments(feedId);
      setComments(response.data);
    } catch (error) {
      
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !selectedFeed) return;

    try {
      await feedAPI.addComment({
        feedId: selectedFeed.id,
        comment: newComment,
        username: user?.username,
      });
      setNewComment('');
      loadComments(selectedFeed.id);
      toast.success('Comment added!');
    } catch (error) {
      toast.error('Failed to add comment');
    }
  };

  const handleDeleteComment = async (num: number) => {
    try {
      await feedAPI.deleteComment(num);
      if (selectedFeed) {
        loadComments(selectedFeed.id);
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
      
      <div className="container mx-auto px-6 py-8 max-w-5xl">
        {/* Toolbar */}
        <div className="mb-6 flex items-center justify-end">
          <Button className="bg-gradient-primary hover:opacity-90" onClick={() => setShowNewPostDialog(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Post
          </Button>
        </div>

        {/* Feed */}
        <div className="space-y-6">
          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
            </div>
          ) : feeds.length === 0 ? (
            <Card className="p-12 text-center">
              <p className="text-muted-foreground">No posts yet. Be the first to share!</p>
            </Card>
          ) : (
            feeds.map((feed) => (
              <Card key={feed.id} className="border-border/50 shadow-lg hover:shadow-xl transition-shadow animate-fade-in">
                <CardHeader>
                  <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback className="bg-gradient-primary text-white">
                            {(feed.username || 'U').charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <Button
                            variant="link"
                            className="p-0 h-auto font-semibold hover:text-primary"
                            onClick={() => loadProfile(feed.username)}
                          >
                            {feed.username || 'Unknown'}
                          </Button>
                          {feed.department && (
                            <p className="text-sm text-muted-foreground">{feed.department}</p>
                          )}
                        </div>
                      </div>
                    {feed.username === user?.username && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeletePost(feed.id)}
                        className="text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <h3 className="text-xl font-bold">{feed.title}</h3>
                  <p className="text-muted-foreground whitespace-pre-wrap">{feed.description}</p>
                </CardContent>
                <CardFooter className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="gap-2"
                    onClick={() => {
                      setSelectedFeed(feed);
                      loadComments(feed.id);
                    }}
                  >
                    <MessageCircle className="h-4 w-4" />
                    Comment
                  </Button>
                </CardFooter>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* New Post Dialog */}
      <Dialog open={showNewPostDialog} onOpenChange={setShowNewPostDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Create a New Post</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              placeholder="Post title..."
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
            />
            <Textarea
              placeholder="What's on your mind?"
              value={newPost.description}
              onChange={(e) => setNewPost({ ...newPost, description: e.target.value })}
              rows={4}
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowNewPostDialog(false)}>Cancel</Button>
              <Button onClick={handleCreatePost} disabled={postLoading} className="bg-gradient-primary hover:opacity-90">
                {postLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Posting...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Post
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Comments Dialog */}
      <Dialog open={!!selectedFeed} onOpenChange={() => setSelectedFeed(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Comments</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* Add Comment */}
            <div className="flex gap-2">
              <Input
                placeholder="Write a comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddComment()}
              />
              <Button onClick={handleAddComment} size="icon" className="bg-gradient-primary">
                <Send className="h-4 w-4" />
              </Button>
            </div>

            {/* Comments List */}
            <div className="space-y-3">
              {comments.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  No comments yet. Be the first to comment!
                </p>
              ) : (
                comments.map((comment) => (
                  <div
                    key={comment.num}
                    className="p-4 rounded-lg bg-secondary/50 flex justify-between items-start"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Avatar className="h-6 w-6">
                          <AvatarFallback className="bg-primary/20 text-primary text-xs">
                            {(comment.username || 'U').charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <Button
                          variant="link"
                          className="p-0 h-auto font-semibold text-sm hover:text-primary"
                          onClick={() => loadProfile(comment.username)}
                        >
                          {comment.username || 'Unknown'}
                        </Button>
                      </div>
                      <p className="text-sm">{comment.comment}</p>
                    </div>
                    {comment.username === user?.username && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteComment(comment.num)}
                        className="text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
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

export default Dashboard;
