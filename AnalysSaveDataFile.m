% Main script
filename = 'HightResolutan2GKir.txt'; % Change this to your data file
data = importData(filename);

% Parameters
T1 = 10000; % Example time value in ms (make sure this value exists in your dataset)
Z_plane = -4.17692; % Example Z plane value in um (make sure this value exists in your dataset)
videoFilename = 'concentration_video.mp4'; % Output video file name
outputFilename = 'concentration_data.csv'; % Output data file name

% Check if T1 and Z_plane exist in the data
if ~ismember(T1, data.Time)
    error('The specified time T1 does not exist in the dataset.');
end
if ~ismember(Z_plane, data.Z)
    error('The specified Z plane does not exist in the dataset.');
end
data.C=2*(5-data.C)+110;
% Filter data for the specified Z plane
zPlaneData = data(data.Z == Z_plane, :);

% Save the filtered data to CSV
writetable(zPlaneData, outputFilename);
disp(['Data saved to: ' outputFilename]);

% Create a figure with two panels and double the width
figure('Position', [100, 100, 1600, 600]); % Set the figure position and size

% Panel 1: Plot concentration distribution at T = T1 and Z plane
subplot(1, 2, 1);
plotConcentrationAtTime(data, T1, Z_plane);

% Panel 2: Create a video showing concentration changes over time for the Z plane
subplot(1, 2, 2);
createConcentrationVideo(data, Z_plane, videoFilename);

% Create new figure for 3D time evolution plots (X and Y)
figure('Position', [100, 100, 1600, 600]);

% Plot time evolution along X and Y
subplot(1, 2, 1);
plot3DTimeEvolution(zPlaneData, 'X');
title('Concentration Evolution Over Time (X-axis)');

subplot(1, 2, 2);
plot3DTimeEvolution(zPlaneData, 'Y');
title('Concentration Evolution Over Time (Y-axis)');

% Function to read data and return it as a table
function data = importData(filename)
    opts = detectImportOptions(filename);
    opts.VariableNamingRule = 'preserve';
    data = readtable(filename, opts);
    % Rename the columns to valid MATLAB identifiers
    data.Properties.VariableNames = {'Time', 'X', 'Y', 'Z', 'C'};
end

% Function to plot the concentration distribution at a specific time and Z-plane
function plotConcentrationAtTime(data, T1, Z_plane)
    % Filter data for the given time and Z plane
    timeData = data(data.Time == T1 & data.Z == Z_plane, :);
    
    % Ensure that timeData is not empty
    if isempty(timeData)
        error('No data found for the specified time and Z plane.');
    end
    
    % Create a grid for X and Y coordinates
    [X, Y] = meshgrid(unique(timeData.X), unique(timeData.Y));
    C = griddata(timeData.X, timeData.Y, timeData.C, X, Y, 'cubic');
    
    % Plot the contour
    contourf(X, Y, C, 'LineColor', 'none');
    colorbar;
    title(['Concentration Distribution at T = ', num2str(T1), ' ms, Z = ', num2str(Z_plane), ' um']);
    xlabel('X (um)');
    ylabel('Y (um)');
    ylabel(colorbar, 'Concentration (mM)');
end

% Function to create a video showing concentration changes over time for a specific Z-plane
function createConcentrationVideo(data, Z_plane, filename)
    % Filter data for the given Z plane
    zData = data(data.Z == Z_plane, :);
    times = unique(zData.Time);
    
    % Ensure that zData is not empty
    if isempty(zData)
        error('No data found for the specified Z plane.');
    end
    
    % Determine the range of concentration values
    cMin = min(zData.C);
    cMax = max(zData.C);
    
    % Create a video writer object
    v = VideoWriter(filename, 'MPEG-4');
    open(v);
    
    % Loop through each time point to create frames
    for t = 1:length(times)
        timeData = zData(zData.Time == times(t), :);
        
        % Create a grid for X and Y coordinates
        [X, Y] = meshgrid(unique(timeData.X), unique(timeData.Y));
        C = griddata(timeData.X, timeData.Y, timeData.C, X, Y, 'cubic');
        
        % Check if the data is constant
        if max(C(:)) == min(C(:))
            warning(['Data at time T = ', num2str(times(t)), ' is constant. Skipping frame.']);
            continue;
        end
        
        % Plot the contour
        contourf(X, Y, C, 'LineColor', 'none');
        colorbar;
        caxis([cMin cMax]); % Set consistent color limits
        title(['Concentration at T = ', num2str(times(t)), ' ms, Z = ', num2str(Z_plane), ' um']);
        xlabel('X (um)');
        ylabel('Y (um)');
        ylabel(colorbar, 'Concentration (mM)');
        
        % Capture the frame and write to video
        frame = getframe(gcf);
        writeVideo(v, frame);
    end
    
    % Close the video writer
    close(v);
end

% Function to create 3D plot showing concentration evolution over time
function plot3DTimeEvolution(data, dimension)
    % Get unique time points and spatial coordinates
    times = unique(data.Time);
    if strcmp(dimension, 'X')
        coords = unique(data.X);
        otherDim = 'Y';
    else % Y dimension
        coords = unique(data.Y);
        otherDim = 'X';
    end
    
    % Create a grid of time and spatial coordinates
    [T, S] = meshgrid(times, coords);
    
    % For each time and spatial coordinate, find the maximum concentration
    C = zeros(size(T));
    for i = 1:length(times)
        for j = 1:length(coords)
            if strcmp(dimension, 'X')
                timeData = data(data.Time == times(i) & data.X == coords(j), :);
            else
                timeData = data(data.Time == times(i) & data.Y == coords(j), :);
            end
            C(j,i) = max(timeData.C);
        end
    end
    
    % Create the 3D surface plot
    surf(T, S, C);
    colormap('jet');
    colorbar;
    
    % Customize the appearance
    xlabel('Time (ms)');
    ylabel([dimension ' Position (um)']);
    zlabel('Concentration (mM)');
    ylabel(colorbar, 'Concentration (mM)');
    
    % Adjust the view
    view(-30, 30);
    grid on;
    
    % Add some lighting effects
    shading interp;
    lighting gouraud;
    camlight;
end