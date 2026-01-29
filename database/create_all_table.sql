-- Test แล้วรันบน pgAdmin ผ่านสร้างตารางได้
-- 01 Create User and Organization
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    user_pw VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(30) NOT NULL,
    user_img TEXT,
    user_socmed TEXT[] NOT NULL
);

CREATE TABLE Orgs (
	org_id SERIAL PRIMARY KEY,
    head_user INT NOT NULL,
    org_name VARCHAR(30) NOT NULL,
    org_img TEXT,

    FOREIGN KEY (head_user) REFERENCES Users(user_id)
);

-- 02 Create Relationship Table for Org Member and User Following

CREATE TABLE UserInOrg (
    user_id INT NOT NULL,
    org_id INT NOT NULL,

    PRIMARY KEY (user_id, org_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (org_id) REFERENCES Orgs(org_id)
);

CREATE TABLE UserFollow (
    user_id INT NOT NULL,
    user_following INT NOT NULL,

    PRIMARY KEY (user_id, user_following),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (user_following) REFERENCES Users(user_id)
);

-- 03 Create Event and Registration Form

CREATE TABLE Events (
    event_id SERIAL PRIMARY KEY,
    event_host INT NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    event_img TEXT,
    event_info TEXT,
    event_map_plain TEXT,
    event_map_decor TEXT,
    event_place VARCHAR(100) NOT NULL,
    event_tags TEXT[],
    booth_apply_info TEXT,
    event_status VARCHAR(30) NOT NULL,
    event_time_start TIMESTAMP NOT NULL,
    event_time_end TIMESTAMP NOT NULL,

    FOREIGN KEY (event_host) REFERENCES Orgs(org_id)
);

CREATE TABLE EventDays (
    eventday_id SERIAL PRIMARY KEY,
    in_event INT NOT NULL,
    event_date DATE NOT NULL,

    FOREIGN KEY (in_event) REFERENCES Events(event_id)
);

CREATE TABLE EventForms (
    form_id SERIAL PRIMARY KEY,
    form_event INT NOT NULL,
    from_question JSON NOT NULL,

    FOREIGN KEY (form_event) REFERENCES Events(event_id)
);

CREATE TABLE FormResponses (
    response_id SERIAL PRIMARY KEY,
    response_submit_by INT NOT NULL,
    response_form INT NOT NULL,
    resp_booth_name VARCHAR(100) NOT NULL,
    resp_booth_cutout TEXT NOT NULL,
    response_answer JSON NOT NULL,

    FOREIGN KEY (response_submit_by) REFERENCES Users(user_id),
    FOREIGN KEY (response_form) REFERENCES EventForms(form_id)
);

-- 04 Create Booth and Relationship

CREATE TABLE BoothLayouts (
    layout_id SERIAL PRIMARY KEY,
    layout_event INT NOT NULL,
    booth_code VARCHAR(10) NOT NULL,
    layout_start_point POINT NOT NULL,
    layout_wide FLOAT NOT NULL,
    layout_long FLOAT NOT NULL,

    FOREIGN KEY (layout_event) REFERENCES Events(event_id)
);

CREATE TABLE Booths (
    booth_id SERIAL PRIMARY KEY,
    booth_menu TEXT[],
    booth_tag VARCHAR(30)[],
    booth_reg_form INT NOT NULL,

    FOREIGN KEY (booth_reg_form) REFERENCES FormResponses(response_id)
);

CREATE TABLE BoothOwner (
    booth_id INT NOT NULL,
    user_id INT NOT NULL,

    PRIMARY KEY (booth_id, user_id),
    FOREIGN KEY (booth_id) REFERENCES Booths(booth_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE BoothInEvent (
    booth_id INT NOT NULL,
    booth_day INT NOT NULL,
    booth_position INT NOT NULL,

    PRIMARY KEY (booth_day, booth_position),
    FOREIGN KEY (booth_id) REFERENCES Booths(booth_id),
    FOREIGN KEY (booth_day) REFERENCES EventDays(eventday_id),
    FOREIGN KEY (booth_position) REFERENCES BoothLayouts(layout_id)
);

-- 05 Create Item and ShoppingList

CREATE TABLE Items(
    item_id SERIAL PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    item_price FLOAT NOT NULL,
    item_img TEXT,
    item_description VARCHAR(255),
    item_tags VARCHAR(30)[],
    item_booth INT NOT NULL,
    item_stock BOOLEAN,

    FOREIGN KEY (item_booth) REFERENCES Booths(booth_id)
);

CREATE TABLE ShoppingLists (
    sl_id SERIAL PRIMARY KEY,
    sl_event_date INT NOT NULL,
    sl_owner INT NOT NULL,

    FOREIGN KEY (sl_event_date) REFERENCES EventDays(eventday_id),
    FOREIGN KEY (sl_owner) REFERENCES Users(user_id)
);

CREATE TABLE ShoppingListItems (
    sl_id INT NOT NULL,
    item_id INT NOT NULL,
    item_count INT NOT NULL,
    item_note VARCHAR(100),
    item_checked BOOLEAN NOT NULL,

    PRIMARY KEY (sl_id, item_id),
    FOREIGN KEY (sl_id) REFERENCES ShoppingLists(sl_id),
    FOREIGN KEY (item_id) REFERENCES Items(item_id)
);