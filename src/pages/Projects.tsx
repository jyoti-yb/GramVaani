import { useEffect, useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { projectAPI, profileAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Plus, Loader2, Trash2, Users, X, Eye, ExternalLink, Mail, Phone, Github, Linkedin } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Project {
  id: number;
  title: string;
  teamLead: string;
  fullName: string;
  description: string;
  date: string;
  maxTeamMembers: number;
  currentTeamMembers: number;
  category: string;
  technologies: string[];
}

interface Application {
  id: number;
  title: string;
  myUsername: string;
  username: string;
  fullName: string;
  applicant?: string; // Full name of the person who applied
  projectName: string;
  description: string;
  technologies: string[];
  accept: boolean;
  category: string;
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

const Projects = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [myApplications, setMyApplications] = useState<Application[]>([]);
  const [requests, setRequests] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [currentTech, setCurrentTech] = useState('');
  const [accepting, setAccepting] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [appliedProjects, setAppliedProjects] = useState<Set<string>>(new Set());
  const [applying, setApplying] = useState(false);
  const [applicationMessage, setApplicationMessage] = useState<string>('');
  const [applyingProjectId, setApplyingProjectId] = useState<number | null>(null);

  const [newProject, setNewProject] = useState({
    title: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    maxTeamMembers: 5,
    category: '',
    technologies: [] as string[],
  });

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    if (!user) return;
    try {
      const [projectsRes, applicationsRes, requestsRes] = await Promise.all([
        projectAPI.getAll(),
        projectAPI.getApplications(user.username),      // SWAPPED: My applications (where I'm the applicant)
        projectAPI.getMyApplications(user.username),    // SWAPPED: Requests to my projects (where I'm the owner)
      ]);
      
      // Ensure all projects have technologies array
      const projectsWithDefaults = (projectsRes.data || []).map((p: any) => ({
        ...p,
        technologies: p.technologies || [],
      }));
      
      // Ensure all applications have required fields
      const applicationsWithDefaults = (applicationsRes.data || []).map((a: any) => ({
        ...a,
        technologies: a.technologies || [],
        myUsername: a.myUsername || 'Unknown',
        username: a.username || 'Unknown',
        fullName: a.fullName || 'Unknown User',
        projectName: a.projectName || 'Untitled Project',
      }));
      
      // For requests, we need applicant info (backend field is `applicant` = applicant username)
      const requestsWithDefaults = await Promise.all(
        (requestsRes.data || []).map(async (r: any) => {
          let applicant = 'Unknown User';
          try {
            // Fetch the applicant's profile to get their full name
            const profileRes = await profileAPI.get(r.applicant);
            applicant = profileRes.data.fullName || r.myUsername;
          } catch (error) {
          }
          
          return {
            ...r,
            technologies: r.technologies || [],
            // Keep `myUsername` in our frontend model as the applicant's username for compatibility
            myUsername: r.applicant || 'Unknown',
            applicant, // Use fetched full name
            projectName: r.projectName || 'Untitled Project',
          };
        })
      );
      
      // Sort projects by date (newest first)
      const sortedProjects = projectsWithDefaults.sort((a: Project, b: Project) => 
        new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime()
      );
      
      setProjects(sortedProjects);
      setMyApplications(applicationsWithDefaults);
      setRequests(requestsWithDefaults);
      
      // Track which projects user has applied to
      const applied = new Set<string>(applicationsWithDefaults.map((a: Application) => a.projectName));
      setAppliedProjects(applied);
    } catch (error) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!newProject.title || !newProject.description || !newProject.category) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      await projectAPI.upload({
        ...newProject,
        teamLead: user?.username,
        fullName: user?.fullName || user?.username,
      });
      toast.success('Project created successfully!');
      setShowCreateDialog(false);
      setNewProject({
        title: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        maxTeamMembers: 5,
        category: '',
        technologies: [],
      });
      loadData();
    } catch (error: any) {
      toast.error('Failed to create project');
    }
  };

  const handleApplyToProject = async (project: Project) => {
  if (appliedProjects.has(project.title)) {
    toast.error('You have already applied to this project');
    return;
  }

  if (!applicationMessage.trim()) {
    toast.error('Please enter a message before applying');
    return;
  }

  setApplying(true);
  try {
    await projectAPI.apply({
      title: project.title,
      myUsername: user?.username,
      username: project.teamLead,
      fullName: project.fullName,
      projectName: project.title,
      description: applicationMessage,
      technologies: [],
      category: project.category,
    });

    setAppliedProjects(prev => new Set(prev).add(project.title));
    toast.success('Application submitted successfully!');
    setApplicationMessage(''); // clear after applying
    setApplyingProjectId(null);
    loadData();
  } catch (error) {
    toast.error('Failed to submit application');
  } finally {
    setApplying(false);
  }
};


  const handleAcceptApplicant = async (application: Application) => {
    setAccepting(application.id);
    try {
      await projectAPI.acceptApplicant({
        ...application,
        accept: true,
      });
      
      // Update local state to prevent duplicate accepts
      setRequests(prev => prev.filter(r => r.id !== application.id));
      
      toast.success('Applicant accepted!');
      loadData();
    } catch (error) {
      toast.error('Failed to accept applicant');
    } finally {
      setAccepting(null);
    }
  };

  const handleDeleteProject = async (projectId: number) => {
  if (!confirm('Are you sure? This will delete the project and all applications.')) return;

  setDeleting(projectId.toString());
  try {
    await projectAPI.delete(projectId);  // must send ID
    toast.success('Project deleted successfully');

    // Update frontend state
    //setProjects(prev => prev.filter(p => p.id !== projectId));

    // Reload all data to sync applications and requests
    await loadData();
  } catch (error) {
    toast.error('Failed to delete project');
  } finally {
    setDeleting(null);
  }
};




  const loadProfile = async (username: string) => {
    try {
      const response = await profileAPI.get(username);
      const profileData = response.data;
      
      // Ensure profile has all required fields with defaults
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

  const addTech = () => {
    if (!currentTech.trim()) return;
    setNewProject({ ...newProject, technologies: [...newProject.technologies, currentTech] });
    setCurrentTech('');
  };

  const removeTech = (index: number) => {
    setNewProject({ ...newProject, technologies: newProject.technologies.filter((_, i) => i !== index) });
  };

  const myProjects = projects.filter((p) => p.teamLead === user?.username);
  const availableProjects = projects.filter((p) => p.teamLead !== user?.username);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold bg-gradient-hero bg-clip-text text-transparent">
            Projects
          </h1>
          <Button onClick={() => setShowCreateDialog(true)} className="bg-gradient-primary hover:opacity-90">
            <Plus className="mr-2 h-4 w-4" />
            Create Project
          </Button>
        </div>

        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="browse">Browse</TabsTrigger>
            <TabsTrigger value="my-applications">My Applications</TabsTrigger>
            <TabsTrigger value="requests">My Requests</TabsTrigger>
          </TabsList>

          {/* Browse Projects */}
          <TabsContent value="browse" className="space-y-6">
            {/* My Projects */}
            {myProjects.length > 0 && (
              <div>
                <h2 className="text-2xl font-semibold mb-4">My Projects</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {myProjects.map((project) => (
                    <Card key={project.id} className="border-border/50 shadow-lg hover:shadow-xl transition-all">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-xl">{project.title}</CardTitle>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteProject(project.id)}
                            className="text-destructive hover:bg-destructive/10"
                            disabled={deleting === project.id.toString()}
                          >
                            {deleting === project.id.toString() ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                        <Badge variant="secondary">{project.category}</Badge>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground line-clamp-3">{project.description}</p>
                        <div className="flex items-center gap-2 text-sm">
                          <Users className="h-4 w-4 text-primary" />
                          <span>{project.currentTeamMembers}/{project.maxTeamMembers} members</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {(project.technologies || []).map((tech, i) => (
                            <Badge key={i} variant="outline">{tech}</Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Available Projects */}
            <div>
              <h2 className="text-2xl font-semibold mb-4">Available Projects</h2>
              {loading ? (
                <div className="text-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                </div>
              ) : availableProjects.length === 0 ? (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground">No projects available</p>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {availableProjects.map((project) => (
                    <Card key={project.id} className="border-border/50 shadow-lg hover:shadow-xl transition-all">
                      <CardHeader>
                        <CardTitle className="text-xl">{project.title}</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">{project.category}</Badge>
                        </div>
                         <div className="flex items-center gap-1">
                          <span className="text-sm text-muted-foreground">by</span>
                          <Button
                            variant="link"
                            className="p-0 h-auto text-sm text-muted-foreground hover:text-primary"
                            onClick={() => loadProfile(project.teamLead)}
                          >
                            {project.fullName || 'Unknown'}
                          </Button>
                        </div>
                        {project.date && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Posted {new Date(project.date).toLocaleDateString()}
                          </p>
                        )}
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground line-clamp-3">{project.description}</p>
                        <div className="flex items-center gap-2 text-sm">
                          <Users className="h-4 w-4 text-primary" />
                          <span>{project.currentTeamMembers}/{project.maxTeamMembers} members</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {(project.technologies || []).map((tech, i) => (
                            <Badge key={i} variant="outline">{tech}</Badge>
                          ))}
                        </div>
                      </CardContent>
                      <CardFooter>
  {!appliedProjects.has(project.title) && (
    <div className="space-y-2 w-full">
      <Textarea
        placeholder="Write a message to the project owner..."
        value={applyingProjectId === project.id ? applicationMessage : ''}
        onChange={(e) => {
          setApplyingProjectId(project.id);
          setApplicationMessage(e.target.value);
        }}
        rows={2}
        className="mb-2 w-full"
      />
      <Button
        onClick={() => handleApplyToProject(project)}
        className="w-full bg-gradient-primary hover:opacity-90"
        disabled={applying}
      >
        {applying ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Submitting...
          </>
        ) : (
          'Apply to Join'
        )}
      </Button>
    </div>
  )}
  {appliedProjects.has(project.title) && (
    <Button disabled className="w-full bg-gray-400">
      Applied
    </Button>
  )}
</CardFooter>

                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          {/* My Applications */}
          <TabsContent value="my-applications" className="space-y-6">
            {myApplications.length === 0 ? (
              <Card className="p-12 text-center">
                <p className="text-muted-foreground">You haven't applied to any projects yet</p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {myApplications.map((app) => (
                  <Card key={app.id} className="border-border/50 shadow-lg">
                    <CardHeader>
                      <CardTitle className="text-xl">{app.projectName}</CardTitle>
                      <Badge variant={app.accept ? 'default' : 'secondary'}>
                        {app.accept ? 'Accepted' : 'Pending'}
                      </Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">Project by: {app.fullName}</p>
                      <p className="text-sm">{app.description}</p>
                      <div className="flex flex-wrap gap-2">
                        {(app.technologies || []).map((tech, i) => (
                          <Badge key={i} variant="outline">{tech}</Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* My Requests */}
          <TabsContent value="requests" className="space-y-6">
            {requests.length === 0 ? (
              <Card className="p-12 text-center">
                <p className="text-muted-foreground">No applications yet</p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {requests.map((request) => (
                  <Card key={request.id} className="border-border/50 shadow-lg">
                    <CardHeader>
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback className="bg-gradient-primary text-white">
                            {(request.myUsername || 'U').charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <Button
                            variant="link"
                            className="p-0 h-auto font-semibold text-base hover:text-primary"
                            onClick={() => loadProfile(request.myUsername)}
                          >
                            {request.applicant || request.myUsername || 'Unknown'}
                            <Eye className="ml-1 h-3 w-3" />
                          </Button>
                          <p className="text-sm text-muted-foreground">Applied to: {request.projectName || 'Unknown Project'}</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm">{request.description}</p>
                      <div className="flex flex-wrap gap-2">
                        {(request.technologies || []).map((tech, i) => (
                          <Badge key={i} variant="outline">{tech}</Badge>
                        ))}
                      </div>
                    </CardContent>
                    {!request.accept && (
                      <CardFooter>
                        <Button
                          onClick={() => handleAcceptApplicant(request)}
                          className="w-full bg-gradient-primary hover:opacity-90"
                          disabled={accepting === request.id}
                        >
                          {accepting === request.id ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Accepting...
                            </>
                          ) : (
                            'Accept Applicant'
                          )}
                        </Button>
                      </CardFooter>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Create Project Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Project Title *</Label>
              <Input
                id="title"
                value={newProject.title}
                onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select value={newProject.category} onValueChange={(v) => setNewProject({ ...newProject, category: v })}>
                <SelectTrigger id="category">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Startup">Startup</SelectItem>
                  <SelectItem value="Hobby">Hobby</SelectItem>
                  <SelectItem value="Subject Project">Subject Project</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                rows={4}
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxMembers">Max Team Members</Label>
              <Input
                id="maxMembers"
                type="number"
                min="2"
                value={newProject.maxTeamMembers}
                onChange={(e) => setNewProject({ ...newProject, maxTeamMembers: parseInt(e.target.value) })}
              />
            </div>
            <div className="space-y-2">
              <Label>Technologies</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="Add technology..."
                  value={currentTech}
                  onChange={(e) => setCurrentTech(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTech())}
                />
                <Button type="button" onClick={() => addTech()} size="icon" variant="secondary">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {(newProject.technologies || []).map((tech, i) => (
                  <Badge key={i} variant="secondary" className="gap-1">
                    {tech}
                    <X className="h-3 w-3 cursor-pointer" onClick={() => removeTech(i)} />
                  </Badge>
                ))}
              </div>
            </div>
            <Button onClick={handleCreateProject} className="w-full bg-gradient-primary hover:opacity-90">
              Create Project
            </Button>
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

export default Projects;
