a = 2;
b = 2;
h = 8;

F = transl([0 0 0]);
C = transl([a b h]) * troty(pi);

trplot(C, 'color', 'g', 'frame', 'C');
hold on;
axis([-0.5 0.5 -0.5 0.5 0 1.2]*h);
trplot(F, 'frame', 'F');

cam = CentralCamera('T', C);
