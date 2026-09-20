-- =============================================================================
-- The Down Under News - PostgreSQL Initialization Script
-- Run by Docker Compose on first start (mounted to /docker-entrypoint-initdb.d/)
-- =============================================================================

-- Ensure we're on the right database
\c newspaper_db;

-- =============================================================================
-- Extensions
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- for fuzzy/full-text search
CREATE EXTENSION IF NOT EXISTS "unaccent";  -- normalize accented chars in search

-- =============================================================================
-- ENUM types
-- =============================================================================
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'editor', 'writer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE article_status AS ENUM ('draft', 'published', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE media_type_enum AS ENUM ('image', 'document', 'pdf');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE library_media_type AS ENUM ('image', 'document', 'pdf');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- =============================================================================
-- Tables
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(80)  NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          user_role    NOT NULL DEFAULT 'writer',
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    slug          VARCHAR(120) NOT NULL UNIQUE,
    description   TEXT,
    display_order INTEGER      NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS articles (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR(500)   NOT NULL,
    slug                VARCHAR(600)   NOT NULL UNIQUE,
    subtitle            VARCHAR(500),
    content             TEXT           NOT NULL,
    excerpt             TEXT,
    author_id           INTEGER        REFERENCES users(id) ON DELETE SET NULL,
    category_id         INTEGER        REFERENCES categories(id) ON DELETE SET NULL,
    featured_image_url  VARCHAR(1024),
    status              article_status NOT NULL DEFAULT 'draft',
    published_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    views_count         INTEGER        NOT NULL DEFAULT 0,
    is_featured         BOOLEAN        NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS article_tags (
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    tag_id     INTEGER NOT NULL REFERENCES tags(id)     ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

CREATE TABLE IF NOT EXISTS article_media (
    id            SERIAL PRIMARY KEY,
    article_id    INTEGER        NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    media_url     VARCHAR(1024)  NOT NULL,
    media_type    media_type_enum NOT NULL,
    file_name     VARCHAR(255),
    file_size     INTEGER,
    display_order INTEGER        DEFAULT 0,
    caption       TEXT,
    uploaded_at   TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS media_library (
    id            SERIAL PRIMARY KEY,
    file_name     VARCHAR(255)     NOT NULL,
    original_name VARCHAR(255),
    media_url     VARCHAR(1024)    NOT NULL,
    media_type    library_media_type NOT NULL,
    file_size     INTEGER,
    uploaded_by   INTEGER          REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at   TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comments (
    id           SERIAL PRIMARY KEY,
    article_id   INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    author_name  VARCHAR(150) NOT NULL,
    author_email VARCHAR(255) NOT NULL,
    content      TEXT         NOT NULL,
    is_approved  BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- Indexes
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_articles_status        ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_category      ON articles(category_id);
CREATE INDEX IF NOT EXISTS idx_articles_author        ON articles(author_id);
CREATE INDEX IF NOT EXISTS idx_articles_published_at  ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_featured      ON articles(is_featured) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_articles_slug          ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_articles_search        ON articles USING GIN (to_tsvector('english', title || ' ' || COALESCE(content, '')));
CREATE INDEX IF NOT EXISTS idx_categories_slug        ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_media_library_type     ON media_library(media_type);
CREATE INDEX IF NOT EXISTS idx_comments_article       ON comments(article_id);
CREATE INDEX IF NOT EXISTS idx_comments_approved      ON comments(is_approved);

-- =============================================================================
-- Seed data
-- =============================================================================

-- Default admin user: admin / Admin@1234
-- Password hash for "Admin@1234" generated with bcrypt (cost=12)
INSERT INTO users (username, email, password_hash, role, first_name, last_name, is_active)
VALUES (
    'admin',
    'admin@thedownundernews.it.com',
    '$2b$12$yzS6j./cGOHbBx194RsziuxMT2.zt8vwf.O3e3ZesNSQL50cBDp6G',
    'admin',
    'Site',
    'Administrator',
    TRUE
),
(
    'writer',
    'writer@thedownundernews.it.com',
    '$2b$12$yzS6j./cGOHbBx194RsziuxMT2.zt8vwf.O3e3ZesNSQL50cBDp6G',
    'writer',
    'Steve',
    'Harvey',
    TRUE
),
(
    'editor',
    'editor@thedoAdministratorwnundernews.it.com',
    '$2b$12$yzS6j./cGOHbBx194RsziuxMT2.zt8vwf.O3e3ZesNSQL50cBDp6G',
    'editor',
    'Editor',
    'Admin',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- Default categories
INSERT INTO categories (name, slug, description, display_order) VALUES
    ('Politics',      'politics',      'National and international political news',   1),
    ('Business',      'business',      'Finance, economy, and business updates',      2),
    ('Technology',    'technology',    'Tech industry news and innovations',           3),
    ('Sports',        'sports',        'Australian and international sports coverage', 4),
    ('Entertainment', 'entertainment', 'Movies, music, culture, and lifestyle',       5),
    ('Science',       'science',       'Science, environment, and discovery',         6),
    ('World',         'world',         'International news and global affairs',       7),
    ('Opinion',       'opinion',       'Editorials and opinion pieces',               8)
ON CONFLICT (slug) DO NOTHING;

-- Sample articles
INSERT INTO articles (title, slug, subtitle, content, excerpt, author_id, category_id, status, published_at, is_featured, views_count)
VALUES (
    'Welcome to The Down Under News',
    'welcome-to-the-down-under-news',
    'Australia''s newest independent online newspaper',
    '<p>Welcome to <strong>The Down Under News</strong>, your trusted source for Australian and global news coverage.</p>
    <p>We are committed to delivering accurate, timely, and unbiased reporting on the stories that matter most to Australians. From politics and business to sports and entertainment, we have got you covered.</p>
    <h2>Our Mission</h2>
    <p>The Down Under News was founded with a simple mission: to provide Australians with high-quality journalism that informs, engages, and empowers.</p>
    <h2>What to Expect</h2>
    <ul>
    <li>Breaking news updated throughout the day</li>
    <li>In-depth analysis and investigative journalism</li>
    <li>Opinion pieces from respected voices</li>
    <li>Comprehensive sports coverage</li>
    <li>Business and technology updates</li>
    </ul>
    <p>Thank you for choosing The Down Under News as your news source. We look forward to keeping you informed.</p>',
    'Welcome to The Down Under News – your trusted source for Australian and global news coverage.',
    1,
    (SELECT id FROM categories WHERE slug = 'politics'),
    'published',
    NOW(),
    TRUE,
    42
),
(
    'Australian Economy Shows Strong Growth in Q3',
    'australian-economy-strong-growth-q3',
    'GDP expands by 2.1% as employment reaches record highs',
    '<p>Australia''s economy demonstrated remarkable resilience in the third quarter, with GDP expanding by 2.1% — exceeding analyst expectations of 1.7%.</p>
    <p>The Reserve Bank of Australia attributed the growth to strong consumer spending, robust exports, and a recovering housing market.</p>
    <h2>Key Highlights</h2>
    <ul>
    <li>GDP growth: 2.1% (forecast: 1.7%)</li>
    <li>Unemployment rate: 3.8% (lowest in 15 years)</li>
    <li>Consumer confidence index: 108.3</li>
    <li>Exports up 4.2% year-on-year</li>
    </ul>
    <p>Treasurer commented that the figures demonstrate Australia''s economic fundamentals remain strong despite global headwinds.</p>',
    'Australia''s economy expanded 2.1% in Q3, beating forecasts as employment reaches record highs.',
    1,
    (SELECT id FROM categories WHERE slug = 'business'),
    'published',
    NOW() - INTERVAL '1 day',
    FALSE,
    156
),
(
    'Tech Giants Invest $2 Billion in Australian AI Research',
    'tech-giants-invest-2-billion-australian-ai',
    'Major technology companies announce landmark investment in local AI capabilities',
    '<p>A consortium of major technology companies has announced a landmark $2 billion investment in Australian artificial intelligence research and development over the next five years.</p>
    <p>The investment will fund new research centres in Sydney, Melbourne, and Brisbane, with an estimated 5,000 new jobs to be created.</p>
    <h2>Investment Breakdown</h2>
    <p>The funds will be directed towards machine learning research, quantum computing, and ethical AI development frameworks.</p>
    <p>Australian universities will partner with the initiative, offering sponsored PhD programs and research fellowships.</p>',
    'Technology companies announce $2 billion investment in Australian AI research centres, creating 5,000 jobs.',
    1,
    (SELECT id FROM categories WHERE slug = 'technology'),
    'published',
    NOW() - INTERVAL '2 days',
    TRUE,
    289
)
ON CONFLICT (slug) DO NOTHING;

-- Additional seed articles
INSERT INTO articles (title, slug, subtitle, content, excerpt, author_id, category_id, status, published_at, is_featured, views_count)
VALUES
(
    'Australia Wins Back-to-Back Test Series Against England',
    'australia-wins-back-to-back-test-series-england',
    'Dominant bowling display seals a stunning 3-1 victory at the MCG',
    '<p>Australia has retained the Ashes trophy with a crushing 3-1 series win over England, capping off a commanding performance at the Melbourne Cricket Ground before a sold-out crowd of 87,000 fans.</p>
    <p>Pat Cummins led from the front with a five-wicket haul in the final innings, wrapping up the series on day four of the fifth Test.</p>
    <h2>Match Summary</h2>
    <p>Australia posted 412 in their first innings, anchored by a brilliant century from Steve Smith. England''s fragile batting lineup crumbled for 198, and despite a brief second-innings fightback, Australia''s pace attack proved relentless.</p>
    <h2>Player of the Series</h2>
    <p>Mitchell Starc was awarded Player of the Series for his 28 wickets across the five Tests, a performance widely regarded as one of the finest in modern Ashes history.</p>
    <p>"This team has incredible depth and character," Cummins said at the post-match presentation. "We never doubted ourselves even when England applied pressure."</p>',
    'Australia retains the Ashes 3-1 with a dominant Test series win, as Cummins claims five wickets in the decider.',
    1,
    (SELECT id FROM categories WHERE slug = 'sports'),
    'published',
    NOW() - INTERVAL '3 days',
    TRUE,
    521
),
(
    'New High-Speed Rail Link to Connect Sydney and Melbourne by 2031',
    'high-speed-rail-sydney-melbourne-2031',
    'Federal government commits $48 billion to transformative infrastructure project',
    '<p>The federal government has officially committed $48 billion to build a high-speed rail corridor connecting Sydney and Melbourne, with services expected to begin in 2031.</p>
    <p>The project, the largest single infrastructure investment in Australian history, will cut travel time between the two cities from roughly eleven hours by conventional rail to under three hours.</p>
    <h2>Key Details</h2>
    <ul>
    <li>Top speed: 320 km/h</li>
    <li>Stations: Sydney, Canberra, Albury-Wodonga, Melbourne</li>
    <li>Estimated daily passenger capacity: 40,000</li>
    <li>Construction jobs: approximately 22,000</li>
    </ul>
    <h2>Environmental Goals</h2>
    <p>The line will run on 100% renewable electricity sourced from new solar farms built alongside the corridor, making it one of the greenest major rail projects in the world.</p>
    <p>Environmental groups have broadly welcomed the project while calling for robust biodiversity offset commitments before construction begins.</p>',
    'The federal government commits $48 billion to a Sydney–Melbourne high-speed rail line, promising a sub-three-hour journey by 2031.',
    1,
    (SELECT id FROM categories WHERE slug = 'politics'),
    'published',
    NOW() - INTERVAL '4 days',
    FALSE,
    378
),
(
    'Great Barrier Reef Records Highest Coral Cover in 36 Years',
    'great-barrier-reef-highest-coral-cover-36-years',
    'Surveyor findings offer cautious optimism amid ongoing climate concerns',
    '<p>The Australian Institute of Marine Science (AIMS) has released its annual survey showing that coral cover across the northern and central sections of the Great Barrier Reef has reached its highest level in 36 years of monitoring.</p>
    <p>Hard coral cover in the northern region reached 36%, while the central region recorded 33% — both significant increases from figures recorded just five years ago.</p>
    <h2>What''s Driving the Recovery?</h2>
    <p>Scientists attribute the rebound largely to a reprieve from mass bleaching events and reduced crown-of-thorns starfish populations following targeted culling programs.</p>
    <p>"This is genuinely encouraging data," said Dr. Mike Emslie, lead researcher at AIMS. "But we must be clear-eyed — the reef remains highly vulnerable to warming sea temperatures, and we cannot become complacent."</p>
    <h2>Ongoing Threats</h2>
    <p>The southern reef, which has experienced repeated bleaching events linked to El Niño conditions, continues to show below-average recovery, reminding observers that the reef''s future remains tied to global climate action.</p>',
    'AIMS data shows Great Barrier Reef coral cover at a 36-year high, but scientists warn the reef remains vulnerable to climate change.',
    1,
    (SELECT id FROM categories WHERE slug = 'science'),
    'published',
    NOW() - INTERVAL '5 days',
    TRUE,
    634
),
(
    'Cost of Living Crisis: Grocery Prices Up 11% Year-on-Year',
    'cost-of-living-crisis-grocery-prices-up-11-percent',
    'Households are cutting back on essentials as supermarket profits soar',
    '<p>New figures from the Australian Bureau of Statistics show that grocery prices have risen 11.2% over the past twelve months, squeezing family budgets at a time when wage growth has averaged just 4.1%.</p>
    <p>The data, compiled from a basket of 200 common household goods, reveals that staples like bread (+14%), dairy (+18%), and fresh vegetables (+22%) have recorded the steepest price rises.</p>
    <h2>Supermarket Profits Under Scrutiny</h2>
    <p>The price surge comes as both Woolworths and Coles posted record after-tax profits in their most recent annual reports, prompting renewed calls from consumer advocates for a federal inquiry into supermarket pricing practices.</p>
    <p>"Australians cannot afford to eat properly while shareholders pocket billions," said Choice CEO Alan Kirkland. "An independent watchdog with real teeth is long overdue."</p>
    <h2>Government Response</h2>
    <p>The Prime Minister has pledged to introduce a mandatory grocery price reporting code before the end of the parliamentary year, though opposition figures have dismissed the move as insufficient.</p>',
    'ABS data shows grocery prices up 11.2% year-on-year, with bread, dairy, and vegetables recording the steepest rises.',
    1,
    (SELECT id FROM categories WHERE slug = 'business'),
    'published',
    NOW() - INTERVAL '6 days',
    FALSE,
    812
),
(
    'Local Band ''The Red Gum Revival'' Signs with Universal Music',
    'red-gum-revival-signs-universal-music',
    'Melbourne indie quartet land global deal after viral social media moment',
    '<p>Melbourne indie-folk quartet The Red Gum Revival have signed a global recording and distribution deal with Universal Music Group, following a whirlwind six months that saw their debut single amass over 40 million streams.</p>
    <p>The band — comprising lead vocalist Jade Nguyen, guitarist Tom Hartley, bassist Amara Osei, and drummer Callum Reid — formed just three years ago in a Fitzroy share house and self-released their first EP on Bandcamp.</p>
    <h2>The Viral Moment</h2>
    <p>Their breakthrough came when a busking video of their song "Red Dust Highway" was shared by a prominent US music influencer, racking up 12 million views in 48 hours and landing them on Spotify''s Global Viral 50 chart.</p>
    <h2>What''s Next</h2>
    <p>The band will record their debut full-length album at Studios 301 in Sydney before embarking on a world tour kicking off in London in April.</p>
    <p>"We still can''t quite believe it," Jade told The Down Under News. "Six months ago we were arguing about who hadn''t done the washing up. Now we''re flying to LA next week."</p>',
    'Melbourne indie-folk band The Red Gum Revival sign with Universal Music Group after their debut single tops 40 million streams.',
    1,
    (SELECT id FROM categories WHERE slug = 'entertainment'),
    'published',
    NOW() - INTERVAL '7 days',
    FALSE,
    295
),
(
    'UN Security Council Backs New Pacific Climate Resilience Fund',
    'un-security-council-pacific-climate-resilience-fund',
    'Historic resolution pledges $10 billion to help island nations adapt to rising seas',
    '<p>The United Nations Security Council has unanimously adopted a landmark resolution establishing a $10 billion Pacific Climate Resilience Fund, marking the first time the body has formally acted on small-island climate adaptation financing.</p>
    <p>The fund will be administered by the Green Climate Fund and will prioritise grants — rather than loans — for Pacific Island nations at the highest risk of displacement due to rising sea levels.</p>
    <h2>Australia''s Role</h2>
    <p>Australia has pledged $1.2 billion to the fund over five years, making it the second-largest contributor after the European Union. Foreign Minister Penny Wong, speaking from New York, described the moment as "a turning point in our relationship with the Pacific."</p>
    <h2>Reactions from the Region</h2>
    <p>Leaders from Tuvalu, Kiribati, and the Marshall Islands — who had lobbied intensively for the fund — welcomed the resolution but cautioned that implementation speed would be critical.</p>
    <p>"Money on paper does not save a home from floodwaters," said Tuvalu Prime Minister Feleti Teo. "We need funds reaching communities within months, not decades."</p>',
    'The UN Security Council unanimously backs a $10 billion Pacific Climate Resilience Fund, with Australia contributing $1.2 billion.',
    1,
    (SELECT id FROM categories WHERE slug = 'world'),
    'published',
    NOW() - INTERVAL '8 days',
    FALSE,
    447
),
(
    'Quantum Computing Breakthrough by University of Sydney Team',
    'quantum-computing-breakthrough-university-sydney',
    'Researchers achieve 99.9% gate fidelity on a 50-qubit processor',
    '<p>Researchers at the University of Sydney''s Nanoscience Institute have announced a major quantum computing breakthrough, achieving 99.9% two-qubit gate fidelity on a 50-qubit silicon-based processor — a threshold long considered the key milestone for fault-tolerant quantum computation.</p>
    <p>The result, published today in <em>Nature</em>, was independently verified by teams at MIT and ETH Zurich.</p>
    <h2>Why It Matters</h2>
    <p>Gate fidelity determines how reliably a quantum computer can perform operations without introducing errors. Reaching 99.9% on 50 qubits opens the door to practical applications in drug discovery, materials science, financial modelling, and cryptography.</p>
    <h2>Industry Implications</h2>
    <p>Major technology companies, including IBM and Google, have publicly acknowledged the result as "a significant step forward." Two Australian quantum start-ups — Q-CTRL and Silicon Quantum Computing — are already in discussions with the university about commercialisation pathways.</p>
    <p>Lead researcher Professor Michelle Simmons said the team aimed to scale to 100 qubits within two years. "Australia is no longer watching the quantum race from the sidelines," she said. "We are at the front."</p>',
    'University of Sydney researchers hit 99.9% two-qubit gate fidelity on a 50-qubit processor, a milestone for fault-tolerant quantum computing.',
    1,
    (SELECT id FROM categories WHERE slug = 'technology'),
    'published',
    NOW() - INTERVAL '9 days',
    TRUE,
    903
),
(
    'Why Australia''s Housing Market Needs a Structural Rethink',
    'australia-housing-market-structural-rethink-opinion',
    'Incremental fixes are no longer enough — it''s time for bold reform',
    '<p>For two decades, successive Australian governments have tinkered at the edges of the housing crisis. First-home buyer grants, stamp duty concessions, shared equity schemes — each announced with fanfare, each proving inadequate within years of launch.</p>
    <p>The uncomfortable truth that politicians of all stripes have been reluctant to confront is this: Australia''s housing market is broken by design, not by accident.</p>
    <h2>The Demand-Side Obsession</h2>
    <p>Nearly every major housing policy intervention in recent memory has focused on helping buyers access a market whose prices continue to outpace wages. This is demand-side tinkering applied to a supply-side problem. Pouring money into grants simply pushes prices higher, enriching existing owners at the expense of aspiring ones.</p>
    <h2>What Structural Reform Looks Like</h2>
    <p>Real reform means tackling negative gearing and capital gains tax concessions that have systematically incentivised property speculation over productive investment. It means reforming zoning laws that strangle medium-density development in inner and middle suburbs. It means adequately funding social housing — not as a safety net of last resort, but as a permanent, well-maintained tenure option for low- and middle-income earners.</p>
    <p>None of this is politically easy. All of it is economically necessary. The longer we wait, the steeper the eventual correction — and the heavier the human cost.</p>',
    'After two decades of demand-side tinkering, it is time for Australia to pursue bold structural housing reform.',
    1,
    (SELECT id FROM categories WHERE slug = 'opinion'),
    'published',
    NOW() - INTERVAL '10 days',
    FALSE,
    567
),
(
    'Northern Territory Records Driest Wet Season in a Century',
    'northern-territory-driest-wet-season-century',
    'Darwin meteorologists link prolonged dry spell to shifting Indian Ocean patterns',
    '<p>The Northern Territory has just emerged from its driest wet season since records began in 1911, with Darwin receiving only 62% of its average rainfall between October and March.</p>
    <p>Bureau of Meteorology senior climatologist Dr. Claire Watson said the anomaly was connected to a persistent negative Indian Ocean Dipole pattern that redirected moisture away from northern Australia throughout the season.</p>
    <h2>Impact on Communities</h2>
    <p>Remote Indigenous communities that rely on seasonal rains for freshwater replenishment are reporting critically low reservoir levels. The Northern Land Council has called for emergency federal water supply infrastructure funding to prevent a humanitarian shortfall in the coming dry season.</p>
    <h2>Wildfire Risk</h2>
    <p>Rangers and fire authorities have issued elevated early-season wildfire warnings for the Top End, with dry grass fuel loads well above average. Prescribed burning programs have been accelerated in an attempt to reduce fuel accumulation before temperatures climb in April.</p>
    <p>"This season has been a stark reminder that climate variability in northern Australia is intensifying," Dr. Watson said. "We cannot plan on average conditions anymore."</p>',
    'Darwin records its driest wet season since 1911, raising concerns about freshwater supply and early wildfire risk across the Northern Territory.',
    1,
    (SELECT id FROM categories WHERE slug = 'science'),
    'published',
    NOW() - INTERVAL '11 days',
    FALSE,
    334
)
ON CONFLICT (slug) DO NOTHING;

-- Sample tags
INSERT INTO tags (name, slug) VALUES
    ('Breaking', 'breaking'),
    ('Australia', 'australia'),
    ('Economy', 'economy'),
    ('Technology', 'technology'),
    ('Politics', 'politics'),
    ('Sports', 'sports')
ON CONFLICT (slug) DO NOTHING;

-- ========================================================================== --
-- Trigger: auto-update updated_at on articles and users
-- ========================================================================== --
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_articles_updated_at ON articles;
CREATE TRIGGER trg_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
