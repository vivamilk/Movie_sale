create table users
(
  userID      INTEGER primary key,
  username    VARCHAR(20) unique not null,
  password    VARCHAR(100) not null,
  is_manager  BOOLEAN
);

create table customer
(
  customerID   INTEGER primary key autoincrement,
  userID       INTEGER references users,
  name         VARCHAR(20) not null,
  emailAddress VARCHAR(30),
  phoneNumber  VARCHAR(16)
);

create table manager
(
  managerID     INTEGER primary key autoincrement,
  userID        INTEGER references users,
  managerLevel  BOOLEAN not null,
  name          VARCHAR(20) not null,
  emailAddress  VARCHAR(30),
  salary        NUMERIC
);

create table store
(
  storeID        INTEGER primary key autoincrement,
  emailAddress   VARCHAR(30) not null,
  region         VARCHAR(30)not null
);

create table management
(
  managerID INTEGER references manager,
  storeID   INTEGER references store,
  primary key (storeID, managerID)
);

create table movie
(
  movieID       INTEGER primary key autoincrement,
  title         VARCHAR(80) not null,
  summary       VARCHAR(1000) not null,
  year          INTEGER(4) not null,
  contentRating VARCHAR(10) not null,
  rating        NUMERIC not null,
  imdbID        VARCHAR(10) unique not null
);

create table genres
(
  movieID INTEGER references movie,
  genre   VARCHAR(20) not null
);

create table stock
(
  storeID     INTEGER references store,
  movieID     INTEGER references movie,
  amount      INTEGER(10) not null,
  amountTemp  INTEGER(10) not null,
  salePrice   NUMERIC not null,
  cost        NUMERIC not null,
  primary key (storeID, movieID)
);

create table shopping_cart
(
  amount      INTEGER(10) not null,
  customerID  INTEGER not null references customer,
  movieID     INTEGER not null references movie,
  storeID     INTEGER not null references store,
  primary key (customerID, movieID, storeID)
);

create table transaction_detail
(
  paypalID     VARCHAR(20) references transaction_info,
  movieID      INTEGER references movie,
  amount       INTEGER(10) not null,
  unitPrice    NUMERIC not null,
  primary key (paypalID, movieID)
);

create table transaction_info
(
  paypalID        VARCHAR(20) primary key,
  purchaseDate    datetime not null,
  customerID      INTEGER references customer,
  storeID         INTEGER references store,
  totalPrice      NUMERIC not null,
  shippingAddress VARCHAR(200) not null,
  -- 0: preparing, 1: shipping, 2: delivered
  status          INTEGER(1) not null,
  check (status>=0 and status<=2)
);