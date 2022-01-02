function f = PlotPhasePortrait(f,xmin,xmax,ymin,ymax)
  % PLOTPHASEPORTRAIT Plots phase portrait of function f with two variables
  % in the domain [xmin, xmax] X [ymin, ymax] using Runge Kutta 4 method
  % with initial time 0, step size 0.125 and 100 steps
  
t0 = 1;
h = 0.125;
n = 100;

% For a range of initial conditions, the Runge Kutta 4 method is called and
% its results are plotted
for y01 = xmin:.5:xmax
    for y02 = ymin:.5:ymax
        y0 = [y01;y02];
        [t,y] = Assignment_4_Pop(f,t0,h,n,y0);
        plot(y(:,1),y(:,2),'-')
        hold on
    end 
end
% axis([xmin xmax ymin ymax])
title('Phase Portrait')
xlabel('x')
ylabel('y')
return