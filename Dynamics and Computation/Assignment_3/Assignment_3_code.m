function [lambda_opt, constant_opt, E] = fit(data, initial_guesses)
% FIT Find data fit
%   [LAMBDA_OPT, CONSTANT_OPT, E] = FIT(DATA, INITIAL_GUESSES) fits a
%   linear combination of exponential functions functions to DATA by
%   minimizing the residue of the least square function, given the 
%   INITIAL_GUESSES for lambda
%
%   [LAMBDA_OPT, CONSTANT_OPT, E] = FIT(DATA, INITIAL_GUESSES) returns a
%   vector LAMBDA_OPT which stores the calculated optimal exponents lambda,
%   a vector CONTANT_OPT , the residue of the fit E, and plots the fit together with the
%   DATA
%   
%   data = (mx2) matrix, where x values are in the first column and y
%   values in the second
%
%   initial_guesses = vector of initial guesses for the exponents (i.e.
%   lambda values)

x_data = data(:,1); % Extracts first column from the data as x values
y_data = data(:,2); % Extracts second column from the data as y values

% (1.) Creates a function of fixed initial_guesses that uses the least
% square method to compute the corresponding residue (i.e. R(λ)), by
% referening the method RESIDUE(DATA,INITIAL_GUESSES)
fun = @(initial_guesses) residue(data, initial_guesses);

% (2.) Computes the optimal exponents lambda by minimizing the value of the
% residue function (i.e. min R(λ))
lambda_opt = fminsearch(fun, initial_guesses);

% Optimal constants C are derived solving the system of linear equations 
% exponents*C=y
constant_opt = mldivide(exp(x_data*lambda_opt),y_data);

% Matrix form: first, the exponent is computed as x times INITIAL_GUESSES
% and it is multiplied with the optimal constant C
y_estimates = exp(x_data*lambda_opt) * constant_opt;

% Real values of y are subtracted from the estimates, then squared and
% added together to get the total residue of the fit, according to the 
% least square method
E = sum((y_data-y_estimates).^2);

% The estimates are plotted over the original data
hold on;
plot(x_data, y_data, '.');
plot(x_data, y_estimates, '-r', 'LineWidth', 2) ;
title('Plot of data and fit');
xlabel('x');
ylabel('y');
hold off;

return