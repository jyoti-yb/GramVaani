import { useEffect, useState, useRef } from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { teamsAPI, profileAPI, groupAPI, CHAT_WS_URL } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import { Plus, Loader2, Trash2, Users, Eye, MessageSquare, Send, ExternalLink, Github, Linkedin, Phone } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';
import { Textarea } from '@/components/ui/textarea';

interface Team {
  teamName: string;
  teamLead: string;
  maxSize: number;
  currentSize: number;
}

interface TeamApplication {
  id: number;
  teamName: string;
  teamLead: string;
  applicant: string;
  accepted: boolean;
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

interface ChatMessage {
  groupName: string;
  sender: string;
  content: string;
  messageType: 'CHAT' | 'JOIN' | 'LEAVE';
  timestamp: string;
}

const Teams = () => {
  const { user } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [myApplications, setMyApplications] = useState<TeamApplication[]>([]);
  const [requests, setRequests] = useState<TeamApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [showChatDialog, setShowChatDialog] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [newTeam, setNewTeam] = useState({
    teamName: '',
    maxSize: 6,
  });
  const [applying, setApplying] = useState(false);
  const [accepting, setAccepting] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [appliedTeams, setAppliedTeams] = useState<Set<string>>(new Set());

  const stompClientRef = useRef<Client | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadData();
  }, [user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadData = async () => {
    if (!user) return;
    try {
      const teamsRes = await teamsAPI.getAll();
      const teamsWithDefaults = (teamsRes.data || []).map((t: any) => ({
        ...t,
        teamName: t.teamName || 'Unnamed Team',
        teamLead: t.teamLead || 'Unknown',
        maxSize: t.maxSize || 6,
        currentSize: t.currentSize || 0,
      }));
      setTeams(teamsWithDefaults);

      // Load applications by this user to other teams
      const allApplications: TeamApplication[] = [];
      for (const team of teamsWithDefaults) {
        try {
          const appsRes = await teamsAPI.getApplications(team.teamName);
          const teamApps = (appsRes.data || []).filter((app: TeamApplication) => app.applicant === user.username);
          allApplications.push(...teamApps);
        } catch (err) {
        }
      }
      setMyApplications(allApplications);

      // Load applications to my teams
      const myTeamNames = teamsWithDefaults.filter((t: Team) => t.teamLead === user.username);
      const allRequests: TeamApplication[] = [];
      for (const team of myTeamNames) {
        try {
          const reqsRes = await teamsAPI.getApplications(team.teamName);
          allRequests.push(...(reqsRes.data || []));
        } catch (err) {
        }
      }
      setRequests(allRequests);
      
      // Track which teams user has applied to
      const applied = new Set(allApplications.map((a: TeamApplication) => a.teamName));
      setAppliedTeams(applied);
    } catch (error) {
      toast.error('Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async () => {
    if (!newTeam.teamName) {
      toast.error('Please enter a team name');
      return;
    }

    try {
      await teamsAPI.create({
        ...newTeam,
        teamLead: user?.username,
        currentSize: 0,
      });
      toast.success('Team created successfully!');
      setShowCreateDialog(false);
      setNewTeam({ teamName: '', maxSize: 6 });
      loadData();
    } catch (error) {
      toast.error('Failed to create team');
    }
  };

  const handleApplyToTeam = async (team: Team) => {
    // Prevent duplicate applications
    if (appliedTeams.has(team.teamName)) {
      toast.error('You have already applied to this team');
      return;
    }

    setApplying(true);
    try {
      await teamsAPI.apply({
        teamName: team.teamName,
        teamLead: team.teamLead,
        applicant: user?.username,
        accepted: false,
      });
      
      // Immediately update local state
      setAppliedTeams(prev => new Set(prev).add(team.teamName));
      
      toast.success('Application submitted!');
      loadData();
    } catch (error) {
      toast.error('Failed to apply');
    } finally {
      setApplying(false);
    }
  };

  const handleAcceptApplicant = async (applicationId: number, teamName: string) => {
    setAccepting(applicationId);
    try {
      await teamsAPI.acceptApplicant(applicationId);
      
      // Update local state to prevent duplicate accepts
      setRequests(prev => prev.filter(r => r.id !== applicationId));
      
      toast.success('Applicant accepted!');
      loadData();
    } catch (error) {
      toast.error('Failed to accept applicant');
    } finally {
      setAccepting(null);
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

  const handleDeleteTeam = async (teamName: string) => {
    if (!confirm('Are you sure? This will delete the team, all applications, and chat history.')) return;

    setDeleting(teamName);
    try {
      await teamsAPI.delete(teamName);
      toast.success('Team deleted successfully');
      loadData();
    } catch (error) {
      toast.error('Failed to delete team');
    } finally {
      setDeleting(null);
    }
  };

  // Temporarily show a coming-soon dialog instead of opening the live chat
  const joinChat = async (team: Team) => {
    setSelectedTeam(team);
    setShowChatDialog(true);
    setMessages([]);
    // NOTE: WebSocket/chat integration is disabled for now. When ready, re-enable connection logic.
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !stompClientRef.current || !selectedTeam) return;

    stompClientRef.current.publish({
      destination: '/app/chat.sendMessage',
      body: JSON.stringify({
        groupName: selectedTeam.teamName,
        sender: user?.username,
        content: newMessage,
        messageType: 'CHAT',
        timestamp: new Date().toISOString(),
      }),
    });

    setNewMessage('');
  };

  const closeChat = () => {
    if (stompClientRef.current) {
      // Send leave message
      stompClientRef.current.publish({
        destination: '/app/chat.sendMessage',
        body: JSON.stringify({
          groupName: selectedTeam?.teamName,
          sender: user?.username,
          content: `${user?.username} left the chat`,
          messageType: 'LEAVE',
          timestamp: new Date().toISOString(),
        }),
      });

      stompClientRef.current.deactivate();
      stompClientRef.current = null;
    }
    setShowChatDialog(false);
    setMessages([]);
    setSelectedTeam(null);
  };

  const myTeams = teams.filter((t) => t.teamLead === user?.username);
  const availableTeams = teams.filter((t) => t.teamLead !== user?.username);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold bg-gradient-hero bg-clip-text text-transparent">
            Teams
          </h1>
          <Button onClick={() => setShowCreateDialog(true)} className="bg-gradient-primary hover:opacity-90">
            <Plus className="mr-2 h-4 w-4" />
            Create Team
          </Button>
        </div>

        <Tabs defaultValue="browse" className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="browse">Browse</TabsTrigger>
            <TabsTrigger value="my-applications">My Applications</TabsTrigger>
            <TabsTrigger value="requests">My Requests</TabsTrigger>
          </TabsList>

          {/* Browse Teams */}
          <TabsContent value="browse" className="space-y-6">
            {/* My Teams */}
            {myTeams.length > 0 && (
              <div>
                <h2 className="text-2xl font-semibold mb-4">My Teams</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {myTeams.map((team) => (
                    <Card key={team.teamName} className="border-border/50 shadow-lg hover:shadow-xl transition-all">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-xl">{team.teamName}</CardTitle>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDeleteTeam(team.teamName)}
                            className="text-destructive hover:bg-destructive/10"
                            disabled={deleting === team.teamName}
                          >
                            {deleting === team.teamName ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex items-center gap-2 text-sm">
                          <Users className="h-4 w-4 text-primary" />
                          <span>{team.currentSize}/{team.maxSize} members</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-muted-foreground">Led by:</span>
                          <Button
                            variant="link"
                            className="p-0 h-auto text-sm text-muted-foreground hover:text-primary"
                            onClick={() => loadProfile(team.teamLead)}
                          >
                            {team.teamLead}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Available Teams */}
            <div>
              <h2 className="text-2xl font-semibold mb-4">Available Teams</h2>
              {loading ? (
                <div className="text-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                </div>
              ) : availableTeams.length === 0 ? (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground">No teams available</p>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {availableTeams.map((team) => (
                    <Card key={team.teamName} className="border-border/50 shadow-lg hover:shadow-xl transition-all">
                      <CardHeader>
                        <CardTitle className="text-xl">{team.teamName}</CardTitle>
                        <div className="flex items-center gap-1">
                          <span className="text-sm text-muted-foreground">Led by:</span>
                          <Button
                            variant="link"
                            className="p-0 h-auto text-sm text-muted-foreground hover:text-primary"
                            onClick={() => loadProfile(team.teamLead)}
                          >
                            {team.teamLead}
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex items-center gap-2 text-sm">
                          <Users className="h-4 w-4 text-primary" />
                          <span>{team.currentSize}/{team.maxSize} members</span>
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button
                          onClick={() => handleApplyToTeam(team)}
                          className="w-full bg-gradient-primary hover:opacity-90"
                          disabled={appliedTeams.has(team.teamName) || applying}
                        >
                          {applying ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Applying...
                            </>
                          ) : appliedTeams.has(team.teamName) ? (
                            'Applied'
                          ) : (
                            'Apply to Join'
                          )}
                        </Button>
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
                <p className="text-muted-foreground">You haven't applied to any teams yet</p>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {myApplications.map((app) => (
                  <Card key={app.id} className="border-border/50 shadow-lg">
                    <CardHeader>
                      <CardTitle className="text-xl">{app.teamName}</CardTitle>
                      <Badge variant={app.accepted ? 'default' : 'secondary'}>
                        {app.accepted ? 'Accepted' : 'Pending'}
                      </Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">Team lead: {app.teamLead}</p>
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
                            {(request.applicant || 'U').charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <Button
                            variant="link"
                            className="p-0 h-auto font-semibold text-base hover:text-primary"
                            onClick={() => loadProfile(request.applicant)}
                          >
                            {request.applicant}
                            <Eye className="ml-1 h-3 w-3" />
                          </Button>
                          <p className="text-sm text-muted-foreground">Applied to: {request.teamName}</p>
                        </div>
                      </div>
                    </CardHeader>
                    {!request.accepted && (
                      <CardFooter>
                        <Button
                          onClick={() => handleAcceptApplicant(request.id, request.teamName)}
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

      {/* Create Team Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Team</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="teamName">Team Name *</Label>
              <Input
                id="teamName"
                value={newTeam.teamName}
                onChange={(e) => setNewTeam({ ...newTeam, teamName: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="maxSize">Max Team Size</Label>
              <Input
                id="maxSize"
                type="number"
                min="2"
                value={newTeam.maxSize}
                onChange={(e) => setNewTeam({ ...newTeam, maxSize: parseInt(e.target.value) })}
              />
            </div>
            <Button onClick={handleCreateTeam} className="w-full bg-gradient-primary hover:opacity-90">
              Create Team
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Chat Dialog */}
      <Dialog open={showChatDialog} onOpenChange={(open) => !open && closeChat()}>
        <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
          <DialogHeader>
            <DialogTitle>Team Chat: {selectedTeam?.teamName}</DialogTitle>
          </DialogHeader>
          
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center">
              <p className="text-xl font-semibold mb-4">The Group Chat feature will be available soon.</p>
              <p className="text-sm text-muted-foreground mb-6">We're working on realtime collaboration — stay tuned!</p>
              <div className="flex justify-center">
                <Button onClick={() => setShowChatDialog(false)} className="bg-gradient-primary hover:opacity-90">
                  Close
                </Button>
              </div>
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

export default Teams;
