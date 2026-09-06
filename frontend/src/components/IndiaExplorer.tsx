import { useState } from "react";
import {
  MapPin,
  Landmark,
  Music,
  Palette,
  Utensils,
  Sparkles,
} from "lucide-react";

type Region = {
  name: string;
  state: string;
  description: string;
  heritage: string;
  tradition: string;
  art: string;
  cuisine: string;
  festival: string;
};

const regions: Region[] = [
  {
    name: "North India",
    state: "Punjab",
    description:
      "A land of vibrant traditions, spiritual heritage, music and community culture.",
    heritage: "Golden Temple",
    tradition: "Bhangra & Folk Music",
    art: "Phulkari",
    cuisine: "Amritsari Kulcha",
    festival: "Baisakhi",
  },
  {
    name: "West India",
    state: "Rajasthan",
    description:
      "Known for royal architecture, desert traditions, folk arts and colorful festivals.",
    heritage: "Amber Fort",
    tradition: "Rajasthani Folk Dance",
    art: "Blue Pottery",
    cuisine: "Dal Baati Churma",
    festival: "Gangaur",
  },
  {
    name: "South India",
    state: "Tamil Nadu",
    description:
      "A civilization shaped by ancient temples, classical arts and Dravidian heritage.",
    heritage: "Brihadeeswarar Temple",
    tradition: "Bharatanatyam",
    art: "Tanjore Painting",
    cuisine: "Pongal",
    festival: "Pongal",
  },
  {
    name: "East India",
    state: "West Bengal",
    description:
      "A cultural center famous for literature, music, crafts and artistic traditions.",
    heritage: "Victoria Memorial",
    tradition: "Baul Music",
    art: "Kantha",
    cuisine: "Bengali Cuisine",
    festival: "Durga Puja",
  },
];

function IndiaExplorer() {
  const [selected, setSelected] = useState<Region>(regions[0]);

  return (
    <section className="india-explorer">
      <div className="explorer-heading">
        <div>
          <span className="section-label">INTERACTIVE INDIA</span>
          <h2>Explore India's cultural regions.</h2>
        </div>

        <p>
          Select a region to discover the heritage, traditions, art, cuisine
          and festivals that shape its cultural identity.
        </p>
      </div>

      <div className="explorer-layout">
        <div className="india-map-panel">
          <div className="map-background">
            <div className="map-grid"></div>

            <div className="india-shape">
              <span className="map-dot dot-north"></span>
              <span className="map-dot dot-west"></span>
              <span className="map-dot dot-east"></span>
              <span className="map-dot dot-south"></span>

              <div className="india-text">INDIA</div>
              <div className="map-subtitle">CULTURAL LANDSCAPE</div>
            </div>

            <div className="map-label label-north">
              <MapPin size={13} />
              North
            </div>

            <div className="map-label label-west">
              <MapPin size={13} />
              West
            </div>

            <div className="map-label label-east">
              <MapPin size={13} />
              East
            </div>

            <div className="map-label label-south">
              <MapPin size={13} />
              South
            </div>
          </div>

          <div className="region-selector">
            {regions.map((region) => (
              <button
                key={region.state}
                className={
                  selected.state === region.state ? "active-region" : ""
                }
                onClick={() => setSelected(region)}
              >
                {region.state}
              </button>
            ))}
          </div>
        </div>

        <div className="culture-panel">
          <div className="culture-header">
            <div className="culture-icon">
              <Sparkles size={21} />
            </div>

            <div>
              <span>{selected.name}</span>
              <h3>{selected.state}</h3>
            </div>
          </div>

          <p className="culture-description">{selected.description}</p>

          <div className="culture-items">
            <div className="culture-item">
              <Landmark size={19} />
              <div>
                <span>Heritage</span>
                <strong>{selected.heritage}</strong>
              </div>
            </div>

            <div className="culture-item">
              <Music size={19} />
              <div>
                <span>Tradition</span>
                <strong>{selected.tradition}</strong>
              </div>
            </div>

            <div className="culture-item">
              <Palette size={19} />
              <div>
                <span>Art & Craft</span>
                <strong>{selected.art}</strong>
              </div>
            </div>

            <div className="culture-item">
              <Utensils size={19} />
              <div>
                <span>Cuisine</span>
                <strong>{selected.cuisine}</strong>
              </div>
            </div>
          </div>

          <div className="festival-box">
            <span>FEATURED FESTIVAL</span>
            <strong>{selected.festival}</strong>
          </div>

          <button className="region-button">
            Explore {selected.state}
            <MapPin size={16} />
          </button>
        </div>
      </div>
    </section>
  );
}

export default IndiaExplorer;