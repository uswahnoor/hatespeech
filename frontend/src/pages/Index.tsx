import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, History, Shield, BarChart3 } from "lucide-react";
import heroImage from "@/assets/hero-image.jpg";

const Index = () => {
  const features = [
    {
      icon: Search,
      title: "Text Analysis",
      description: "Analyze text content for hate speech and harmful language with AI-powered detection.",
      href: "/detect",
    },
    {
      icon: History,
      title: "Analysis History",
      description: "View your previous text analyses and track patterns over time.",
      href: "/history",
    },
    {
      icon: Shield,
      title: "Content Safety",
      description: "Ensure your platform maintains a safe and welcoming environment.",
      href: "/detect",
    },
    {
      icon: BarChart3,
      title: "Analytics",
      description: "Get insights into content moderation trends and detection accuracy.",
      href: "/history",
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-xl bg-gradient-hero text-white">
        <div className="absolute inset-0">
          <img
            src={heroImage}
            alt="SafeSpeak Dashboard"
            className="w-full h-full object-cover opacity-20"
          />
          <div className="absolute inset-0 bg-gradient-hero opacity-80"></div>
        </div>
        
        <div className="relative px-8 py-16 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Intelligent Content Moderation
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90 max-w-3xl mx-auto">
            Protect your community with AI-powered hate speech detection. 
            Analyze text content in real-time and maintain a safe digital environment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" variant="secondary">
              <Link to="/detect">Start Analysis</Link>
            </Button>
            <Button asChild size="lg" variant="secondary">
              <Link to="/history">View History</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section>
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            Powerful Content Analysis Tools
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to maintain content safety and build trust in your community.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="shadow-soft hover:shadow-glow transition-all duration-300 group">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">
                    {feature.description}
                  </CardDescription>
                  <Button asChild variant="outline" size="sm" className="w-full">
                    <Link to={feature.href}>
                      Learn More
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Quick Actions */}
      <section className="bg-muted/50 rounded-xl p-8">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-foreground mb-4">
            Ready to get started?
          </h3>
          <p className="text-muted-foreground mb-6">
            Begin analyzing content or review your analysis history.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild className="bg-gradient-primary hover:opacity-90">
              <Link to="/detect">
                <Search className="h-4 w-4 mr-2" />
                Analyze Text
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/history">
                <History className="h-4 w-4 mr-2" />
                View History
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
