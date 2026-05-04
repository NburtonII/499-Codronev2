// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// The Unreal ViewportCamera implementation.

#include "UnrealViewportCamera.h"

#include <algorithm>
#include <iterator>
#include <utility>
#include <vector>

#include "Camera/CameraComponent.h"
#include "CineCameraComponent.h"
#include "ProjectAirSim.h"
#include "Runtime/Engine/Classes/Engine/StaticMesh.h"
#include "UnrealHelpers.h"
#include "UnrealLogger.h"
#include "core_sim/clock.hpp"
#include "core_sim/physics_common_types.hpp"
#include "core_sim/transforms/transform.hpp"
#include "core_sim/viewport_camera.hpp"
#include "Engine/EngineTypes.h"
#include "Components/SphereComponent.h"

namespace projectairsim = microsoft::projectairsim;

AUnrealViewportCamera::AUnrealViewportCamera(
    const FObjectInitializer& ObjectInitialize)
    : ACineCameraActor(ObjectInitialize) {
  PrimaryActorTick.bCanEverTick = true;

  CollisionSphere = CreateDefaultSubobject<USphereComponent>(TEXT("CollisionSphere"));
  RootComponent = CollisionSphere;

  GerCineCameraComponent()->SetUpAttachment(CollisionSphere);

  CollisionSphere->InitSphereRadius(5.0f);
  CollisionSphere->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
  CollisionSphere->SetCollisionProfileName(TEXT("BlockAll"));
}

void AUnrealViewportCamera::Initialize(
    projectairsim::ViewportCamera& InViewportCamera) {
  // Set callbacks for the viewport camera topics

  InViewportCamera.SetCallbackPoseUpdated(
      [this](const microsoft::projectairsim::Pose& inPose) {
        this->UpdateViewportCameraTargetPose(inPose);
      });

  InViewportCamera.SetCallbackAspectRatioUpdated([this](float aspectRatio) {
    this->UpdateViewportCameraAspectRatio(aspectRatio);
  });

  InViewportCamera.SetCallbackZoomUpdated(
      [this](float zoom) { this->UpdateViewPortCameraZoom(zoom); });
}

void AUnrealViewportCamera::UpdateViewportCameraTargetPose(
    const projectairsim::Pose& InPose) {
  // TODO Need mutex lock to block writing while these data members are being
  // read in other parts of the code to guarantee pose/timestamp stays in sync?
  ViewportCameraTargetPose = InPose;
  bHasTargetPoseUpdated = true;

  // UnrealLogger::Log(projectairsim::LogLevel::kTrace,
  //                   TEXT("UpdateViewportCameraTargetPose xyz=%f, %f, %f"),
  //                   ViewportCameraTargetPose.position.x(),
  //                   ViewportCameraTargetPose.position.y(),
  //                   ViewportCameraTargetPose.position.z());
}

void AUnrealViewportCamera::MoveViewportCameraToTargetPose() {
  if (bHasTargetPoseUpdated == false) return;

  // Todo later if collisions are added to env_actors

  // Clear robot's has_collided flag before trying to move again
  // sim_robot.SetHasCollided(false);

  // Copy target pose data in case it gets updated again while processing
  projectairsim::Pose TgtPose = ViewportCameraTargetPose;
  bHasTargetPoseUpdated = false;  // done processing target pose, clear flag

  // Use local copy of target pose to do actual env actor pose update
  const FVector TgtLocNEU =
      UnrealHelpers::ToFVector(projectairsim::TransformUtils::NedToNeuLinear(
          projectairsim::TransformUtils::ToCentimeters(TgtPose.position)));
  const FRotator TgtRot = UnrealHelpers::ToFRotator(TgtPose.orientation);
  //Adding Occlusion to the camera
  UWorld* world = getWorld();
  if(world)
  {
    FVector DroneWorldLoc = GetActorLocation();

    FHitResult HitResult;
    FCollisionQUeryParams QueryParams;
    QueryParams.AddIgnoredActor(this);

    bool bhit = World->LineTraceSingleByChannel(
            HitResult,
            DroneWorldLoc,      // trace from drone
            TgtLocNEU,          // to desired camera position
            ECC_Camera,         // camera collision channel
            QueryParams
        );
      FVector SafeCameraLoc = TgtLocNEU;
        if (bHit)
        {
            // Pull camera slightly in front of the hit point
            FVector Dir = (TgtLocNEU - DroneWorldLoc).GetSafeNormal();
            SafeCameraLoc = HitResult.Location - Dir * 20.0f; // 20cm buffer
        }

  }
  // Move UE position
  FHitResult HitResult;
  this->SetActorLocationAndRotation(
    TgtLocNEU, 
    TgtRot,
    true,
    &HitResult);
}

void AUnrealViewportCamera::UpdateViewportCameraAspectRatio(float aspectRatio) {
  if (aspectRatio <= 0) return;
  aspect_ratio = aspectRatio;
  bHasAspectRatioUpdated = true;
}

void AUnrealViewportCamera::MoveViewportCameraToAspectRatio() {
  if (bHasAspectRatioUpdated == false) return;

  UCineCameraComponent* CinemaCameraComponent = this->GetCineCameraComponent();
  if (CinemaCameraComponent) {
    CinemaCameraComponent->Filmback.SensorHeight =
        CinemaCameraComponent->Filmback.SensorWidth / aspect_ratio;
    bHasAspectRatioUpdated = false;
  }
}

void AUnrealViewportCamera::UpdateViewPortCameraZoom(float zoom) {
  if (zoom <= 0) return;
  zoom_ = zoom;
  bHasZoomUpdated = true;
}

void AUnrealViewportCamera::MoveViewportCameraToZoom() {
  if (bHasZoomUpdated == false) return;

  UCineCameraComponent* aCinemaCameraComponent = this->GetCineCameraComponent();
  if (aCinemaCameraComponent) {
    // Zoom = focal length/sensor width
    aCinemaCameraComponent->CurrentFocalLength =
        aCinemaCameraComponent->Filmback.SensorWidth * zoom_;
    bHasZoomUpdated = false;
  }
}

void AUnrealViewportCamera::BeginPlay() { Super::BeginPlay(); }

void AUnrealViewportCamera::EndPlay(const EEndPlayReason::Type EndPlayReason) {
  Super::EndPlay(EndPlayReason);
}

void AUnrealViewportCamera::Tick(float DeltaTime) {
  Super::Tick(DeltaTime);
  // In case of a tick coming through while it should be paused, just return
  if (UGameplayStatics::IsGamePaused(this->GetWorld())) return;
  MoveViewportCameraToTargetPose();
  MoveViewportCameraToAspectRatio();
  MoveViewportCameraToZoom();
}
