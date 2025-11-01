import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MapPin, Phone, Clock, Star, Navigation } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

interface Hospital {
  id: number;
  name: string;
  address: string;
  distance: string;
  rating: number;
  specialties: string[];
  phone: string;
  availability: "immediate" | "today" | "tomorrow";
}

const hospitals: Hospital[] = [
  {
    id: 1,
    name: "Apollo Multispecialty Hospital",
    address: "123 MG Road, Bangalore",
    distance: "1.2 km",
    rating: 4.8,
    specialties: ["Cardiology", "Neurology", "Orthopedics"],
    phone: "+91 80 1234 5678",
    availability: "immediate",
  },
  {
    id: 2,
    name: "Manipal Hospital",
    address: "456 HAL Airport Road, Bangalore",
    distance: "2.5 km",
    rating: 4.6,
    specialties: ["General Medicine", "Pediatrics", "ENT"],
    phone: "+91 80 2345 6789",
    availability: "today",
  },
  {
    id: 3,
    name: "Fortis Hospital",
    address: "789 Bannerghatta Road, Bangalore",
    distance: "3.8 km",
    rating: 4.7,
    specialties: ["Oncology", "Gastroenterology", "Nephrology"],
    phone: "+91 80 3456 7890",
    availability: "tomorrow",
  },
];

export default function Appointments() {
  const navigate = useNavigate();
  const [selectedHospital, setSelectedHospital] = useState<number | null>(null);

  const handleBookAppointment = (hospital: Hospital) => {
    navigate("/agent-call", { state: { hospital } });
  };

  const getAvailabilityBadge = (availability: Hospital["availability"]) => {
    switch (availability) {
      case "immediate":
        return <Badge className="bg-primary">Available Now</Badge>;
      case "today":
        return <Badge variant="secondary">Available Today</Badge>;
      case "tomorrow":
        return <Badge variant="outline">Tomorrow</Badge>;
    }
  };

  return (
    <div className="flex h-full flex-col lg:flex-row">
      {/* Left Side - Map */}
      <div className="relative h-96 w-full border-b border-border bg-muted lg:h-full lg:w-1/2 lg:border-b-0 lg:border-r">
        {/* Mock Map */}
        <div className="flex h-full items-center justify-center bg-gradient-to-br from-primary-lighter to-secondary/20">
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-primary shadow-lg">
              <MapPin className="h-12 w-12 text-primary-foreground" />
            </div>
            <p className="text-lg font-semibold text-foreground">Your Location</p>
            <p className="text-sm text-muted-foreground">Koramangala, Bangalore</p>
            <Button variant="outline" className="mt-4" size="sm">
              <Navigation className="mr-2 h-4 w-4" />
              Update Location
            </Button>
          </div>
        </div>

        {/* Map Overlay - Markers */}
        <div className="absolute left-1/4 top-1/4 animate-bounce">
          <div className="h-8 w-8 rounded-full bg-primary shadow-lg"></div>
        </div>
        <div className="absolute right-1/3 top-1/3 animate-bounce delay-100">
          <div className="h-8 w-8 rounded-full bg-primary shadow-lg"></div>
        </div>
        <div className="absolute bottom-1/3 left-1/3 animate-bounce delay-200">
          <div className="h-8 w-8 rounded-full bg-primary shadow-lg"></div>
        </div>
      </div>

      {/* Right Side - Hospital List */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card px-6 py-5">
          <h1 className="text-2xl font-bold text-foreground">Nearby Hospitals</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {hospitals.length} hospitals within 5 km
          </p>
        </div>

        {/* Hospital List */}
        <div className="flex-1 overflow-auto p-6">
          <div className="space-y-4">
            {hospitals.map((hospital) => (
              <Card
                key={hospital.id}
                className="p-5 transition-smooth hover:shadow-md"
              >
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-foreground">
                        {hospital.name}
                      </h3>
                      <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
                        <MapPin className="h-4 w-4" />
                        <span>{hospital.address}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-sm">
                      <Star className="h-4 w-4 fill-primary text-primary" />
                      <span className="font-medium text-foreground">
                        {hospital.rating}
                      </span>
                    </div>
                  </div>

                  {/* Distance & Availability */}
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">
                      <Navigation className="mr-1 h-3 w-3" />
                      {hospital.distance}
                    </Badge>
                    {getAvailabilityBadge(hospital.availability)}
                  </div>

                  {/* Specialties */}
                  <div className="flex flex-wrap gap-2">
                    {hospital.specialties.map((specialty, idx) => (
                      <span
                        key={idx}
                        className="rounded-full bg-primary-lighter px-3 py-1 text-xs font-medium text-primary"
                      >
                        {specialty}
                      </span>
                    ))}
                  </div>

                  {/* Contact & Book */}
                  <div className="flex items-center justify-between border-t border-border pt-3">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Phone className="h-4 w-4" />
                      <span>{hospital.phone}</span>
                    </div>
                    <Button
                      onClick={() => handleBookAppointment(hospital)}
                      disabled={selectedHospital === hospital.id}
                      size="sm"
                    >
                      {selectedHospital === hospital.id ? (
                        <>
                          <Clock className="mr-2 h-4 w-4 animate-spin" />
                          Booking...
                        </>
                      ) : (
                        "Book Appointment"
                      )}
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
