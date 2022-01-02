function E = residue(data,initial_guesses)
% RESIDUE Find residue of data given the initial lambda guesses (i.e.
% R(lambda))
%   E=RESIDUE(DATA, INITIAL_GUESSES) splits the DATA in x and y, and then 
%   it computes the y estimates. Finally, it subtracts the real y values 
%   from the estimates and adds their squares together to return the sum of
%   residuals
%
%   data = (mx2) matrix, where x values are in the first column and y
%   values in the second
%
%   initial_guesses = vector of initial guesses for the exponents (i.e.
%   lambda values)

x_data = data(:,1); % Extracts first column from the data as x values
y_data = data(:,2); % Extracts second column from the data as y values

% Matrix form: first, the exponent is computed as x times INITIAL_GUESSES,
% then the constants C are derived solving the system of linear equations 
% exponents*C=y, using mldivide, and finally it multiplies the two terms
y_estimates = exp(x_data*initial_guesses) * mldivide(exp(x_data*initial_guesses),y_data);

% Real values of y are subtracted from the estimates, then squared and
% added together to get the total residue of the fit, according to the 
% least square method
E = sum((y_data-y_estimates).^2);

return