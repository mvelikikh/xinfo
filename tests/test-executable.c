typedef struct {
  long nam_len;
  char *nam;
  long xstruct_len;
  char *xstruct;
  short typ;
  short flg;
  int unused3;
  long rsz;
  long unused4;
  int coc;
  int unused5;
  int obj;
  short ver;
  short unused6;
  long unused7;
} kqftab_struct;

typedef struct {
  long unused1;
  void *xstruct;
  void *cb1;
  void *cb2;
} kqftap19_struct;

typedef struct {
  long unused1;
  void *xstruct;
  void *cb1;
  void *cb2;
  long unused2;
} kqftap23_struct;

typedef struct {
  long len;
  char *nam;
  char dty;
  char typ;
  char idx;
  char ipo;
  char max;
  char unused1;
  char unused2;
  char unused3;
  char lsz;
  char unused4;
  char unused5;
  char unused6;
  long lof;
  long siz;
  short off;
  short unused7;
  long kqfcop_indx;
} xcolumn_struct;

kqftab_struct const kqftab[] = {
    {10, "X$TABLEA1", 7, "tablea1", 4, 5, 1, 2, 2, 1, 1, 1, 1, 0, 0},
    {10, "X$TABLEB1", 7, "tableb1", 4, 5, 1, 2, 2, 1, 1, 1, 1, 0, 0},
    {10, "X$TABLEA2", 7, "tablea2", 4, 5, 1, 2, 2, 1, 1, 1, 1, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}};

xcolumn_struct const tablea1_c[] = {
    {4, "COL1", 1, 28, 1, 2, 3, 4, 5, 6, 2, 7, 8, 9, 10, 128, 8, 11, 0},
    {4, "COL2", 2, 11, 1, 2, 3, 4, 5, 6, 2, 7, 8, 9, 10, 1, 32, 11, 1},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}};

void f1() {}
void f2() {}

#define KQFTAP19 {{0, (void *)tablea1_c, f1, f2}, {0, 0, 0, 0}}

kqftap19_struct const kqftap[] = KQFTAP19;
kqftap19_struct const kqftap19[] = KQFTAP19;

kqftap23_struct const kqftap23[] = {{0, (void *)tablea1_c, f1, f2, 0},
                                    {0, 0, 0, 0, 0}};

void *const kqfcop[] = {0, 0, 0, f1};

int main() {}
